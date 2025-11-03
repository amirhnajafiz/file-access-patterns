#!/usr/bin/env sh
# file: trace.sh

# Traces all file access events of a command and its subprocs and outputs the total bytes read/write and access times.
# Usage: 
#   trace -c "command" -o output
#   trace -p pid -o output
#   trace -n name -o output
#   trace -cg cgroupid -o output

set -eu

print_usage() {
  cat <<EOF
Usage:
  $0 -c "command" -o output     # run bpftrace with -c (bpftrace/ctrace.bt)
  $0 -p pid -o output           # attach bpftrace to pid (bpftrace/ptrace.bt)
  $0 -n name -o output          # attach bpftrace by name (bpftrace/ntrace.bt)
  $0 -cg cgroupid -o output # attach bpftrace by name (bpftrace/ctrace_cgid.bt)
Notes:
  - Precedence order is command, pid then name.
  - Requires bpftrace and the scripts ctrace.bt, ptrace.bt and ntrace.bt to exist in
    the current working directory (or edit paths in the script).
EOF
}

# defaults
cmd=""
pid=""
name=""
cgid=""
out=""

# parse options
while getopts ":c:p:n:o:h" opt; do
  case "$opt" in
    c) cmd="$OPTARG" ;;
    p) pid="$OPTARG" ;;
    n) name="$OPTARG" ;;
    cg) cgid="$OPTARG" ;;
    o) out="$OPTARG" ;;
    h) print_usage; exit 0 ;;
    \?) printf "Invalid option: -%s\n\n" "$OPTARG" >&2; print_usage; exit 2 ;;
    :) printf "Option -%s requires an argument.\n\n" "$OPTARG" >&2; print_usage; exit 2 ;;
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
