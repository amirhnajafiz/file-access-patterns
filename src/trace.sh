#!/usr/bin/env sh
# file: trace.sh

# Traces all file access events of a command and its sub-processes,
# and outputs the total bytes read/written and access times.
# 
# Usage examples:
#   trace -c "command"   -o output
#   trace -p pid         -o output
#   trace -n name        -o output
#   trace -cg cgroupid   -o output

set -eu

print_usage() {
  cat <<EOF
Usage:
  $0 -c/--cmd   "command"   -o output     # trace a command and its subprocesses (bpftrace/ctrace.bt)
  $0 -p/--pid   pid         -o output     # trace an existing process by PID (bpftrace/ptrace.bt)
  $0 -n/--name  name        -o output     # trace all processes by name (bpftrace/ntrace.bt)
  $0 -cg/--cgid cgroupid    -o output     # trace processes by cgroup ID (bpftrace/ctrace_cgid.bt)

Notes:
  - Precedence order: command > pid > name > cgroupid
  - Requires bpftrace and the scripts ctrace.bt, ptrace.bt, ntrace.bt,
    and ctrace_cgid.bt to exist in the current working directory.
    (You can edit the paths inside this script if needed.)
EOF
}

# defaults
cmd=""
pid=""
name=""
cgid=""
out=""

# parse options
while [ $# -gt 0 ]; do
  case "$1" in
    -c|--cmd)   cmd="$2"; shift 2 ;;
    -p|--pid)   pid="$2"; shift 2 ;;
    -n|--name)  name="$2"; shift 2 ;;
    -cg|--cgid) cgid="$2"; shift 2 ;;
    -o|--out)   out="$2"; shift 2 ;;
    -h|--help)  print_usage; exit 0 ;;
    *) echo "Unknown option: $1"; print_usage; exit 2 ;;
  esac
done

# require output
if [ -z "$out" ]; then
  printf "Error: output file must be specified with -o\n\n" >&2
  print_usage
  exit 2
fi

# check bpftrace availability
if ! command -v bpftrace >/dev/null 2>&1; then
  printf "Error: bpftrace not found in PATH. Please install bpftrace.\n" >&2
  exit 3
fi

# helper to ensure script file exists
ensure_script() {
  script="$1"
  if [ ! -f "$script" ]; then
    printf "Error: required script '%s' not found.\n" "$script" >&2
    exit 4
  fi
}

# decide what to run
if [ -n "$cmd" ]; then
  ensure_script "scripts/ctrace.bt"
  printf "Running: bpftrace -c %s scripts/ctrace.bt > %s\n" "'$cmd'" "$out"
  # use exec so the shell is replaced by bpftrace (optional). We capture exit code.
  # quoting $cmd carefully so it's passed as a single argument to -c.
  bpftrace -c "$cmd" scripts/ctrace.bt > "$out"
  rc=$?
  if [ $rc -ne 0 ]; then
    printf "bpftrace exited with code %d\n" "$rc" >&2
  fi
  exit $rc

elif [ -n "$pid" ]; then
  ensure_script "scripts/ptrace.bt"
  # validate pid is numeric
  case $pid in
    ''|*[!0-9]*) printf "Error: pid must be a positive integer.\n" >&2; exit 2 ;;
  esac

  printf "Running: bpftrace -p %s scripts/ptrace.bt > %s\n" "$pid" "$out"
  bpftrace scripts/ptrace.bt "$pid" > "$out"
  rc=$?
  if [ $rc -ne 0 ]; then
    printf "bpftrace exited with code %d\n" "$rc" >&2
  fi
  exit $rc

elif [ -n "$name" ]; then
  ensure_script "scripts/ntrace.bt"
  printf "Running: bpftrace scripts/ntrace.bt %s > %s\n" "'$name'" "$out"
  # use exec so the shell is replaced by bpftrace (optional). We capture exit code.
  # quoting $cmd carefully so it's passed as a single argument to -c.
  bpftrace scripts/ntrace.bt "$name" > "$out"
  rc=$?
  if [ $rc -ne 0 ]; then
    printf "bpftrace exited with code %d\n" "$rc" >&2
  fi
  exit $rc 

elif [ -n "$cgid" ]; then
  ensure_script "scripts/ctrace_cgid.bt"
  # validate cgid is numeric
  case $cgid in
    ''|*[!0-9]*) printf "Error: cgroupid must be a positive integer.\n" >&2; exit 2 ;;
  esac

  printf "Running: bpftrace -p %s scripts/ctrace_cgid.bt > %s\n" "$cgid" "$out"
  bpftrace scripts/ctrace_cgid.bt "$cgid" > "$out"
  rc=$?
  if [ $rc -ne 0 ]; then
    printf "bpftrace exited with code %d\n" "$rc" >&2
  fi
  exit $rc

else
  printf "Error: either -c <command>, -p <pid>, -cg <cgroupid> or -n <name> must be provided.\n\n" >&2
  print_usage
  exit 2
fi
