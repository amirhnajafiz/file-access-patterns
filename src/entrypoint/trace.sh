#!/usr/bin/env sh
# file: entrypoint/trace.sh

# Traces all file access events of a command and its sub-processes,
# and outputs the total bytes read/written and access times.
# 
# Usage examples:
#   trace -c "command"   -o output -d
#   trace -p pid         -o output -d
#   trace -n name        -o output -d
#   trace -cg cgroupid   -o output -d

set -eu

print_usage() {
  cat <<EOF
Usage:
  $0 -flag [-o|--output output] [-d|--debug]

Flags:
  -c/--cmd   "command"    # trace a command and its subprocesses (bpftrace/tracings/cmd_trace.bt)
  -p/--pid   pid          # trace an existing process by PID (bpftrace/tracings/pid_trace.bt)
  -n/--name  name         # trace all processes by name (bpftrace/tracings/comm_trace.bt)
  -cg/--cgid cgroupid     # trace processes by cgroup ID (bpftrace/cgroups/cgroup_trace.bt)

Optional flags:
  -o/--out output          File path to export the tracing logs (default is STDOUT)
  -d/--debug                  Display debug lines in bpftrace program
  -cgcmd "command"  Filter based on a command in cgroup tracing (only works when -cg is provided)          

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
cgcmd=""
debug=0

# parse options
while [ $# -gt 0 ]; do
  case "$1" in
    -c|--cmd)   cmd="$2"; shift 2 ;;
    -p|--pid)   pid="$2"; shift 2 ;;
    -n|--name)  name="$2"; shift 2 ;;
    -cg|--cgid) cgid="$2"; shift 2 ;;
    -cgcmd) cgcmd="$2"; shift 2;;
    -o|--out)   out="$2"; shift 2 ;;
    -d|--debug) debug=1; shift 1 ;;
    -h|--help)  print_usage; exit 0 ;;
    *) echo "Unknown option: $1"; print_usage; exit 2 ;;
  esac
done

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
  ensure_script "bpftrace/tracings/cmd_trace.bt"

  if [ -n "$out" ]; then
    bpftrace -o "$out" -c "$cmd" bpftrace/tracings/cmd_trace.bt "$debug"
  else
    bpftrace -c "$cmd" bpftrace/tracings/cmd_trace.bt "$debug"
  fi

  rc=$?
  if [ $rc -ne 0 ]; then
    printf "bpftrace exited with code %d\n" "$rc" >&2
  fi
  exit $rc

elif [ -n "$pid" ]; then
  ensure_script "bpftrace/tracings/pid_trace.bt"

  # validate pid is numeric
  case $pid in
    ''|*[!0-9]*) printf "Error: pid must be a positive integer.\n" >&2; exit 2 ;;
  esac

  if [ -n "$out" ]; then
    bpftrace -o "$out" bpftrace/tracings/pid_trace.bt "$pid" "$debug"
  else
    bpftrace bpftrace/tracings/pid_trace.bt "$pid" "$debug"
  fi

  rc=$?
  if [ $rc -ne 0 ]; then
    printf "bpftrace exited with code %d\n" "$rc" >&2
  fi
  exit $rc

elif [ -n "$name" ]; then
  ensure_script "bpftrace/tracings/comm_trace.bt"

  if [ -n "$out" ]; then
    bpftrace -o "$out" bpftrace/tracings/comm_trace.bt "$name" "$debug"
  else
    bpftrace bpftrace/tracings/comm_trace.bt "$name" "$debug"
  fi

  rc=$?
  if [ $rc -ne 0 ]; then
    printf "bpftrace exited with code %d\n" "$rc" >&2
  fi
  exit $rc 

elif [ -n "$cgid" ]; then
  ensure_script "bpftrace/cgroups/cgroup_trace.bt"
  ensure_script "bpftrace/cgroups/cgroup_comm_trace.bt"

  # validate cgid is numeric
  case $cgid in
    ''|*[!0-9]*) printf "Error: cgroupid must be a positive integer.\n" >&2; exit 2 ;;
  esac

  if [ -n "$cgcmd" ]; then
    if [ -n "$out" ]; then
      bpftrace -o "$out" bpftrace/cgroups/cgroup_trace.bt "$cgid" "$cgcmd" "$debug"
    else
      bpftrace bpftrace/cgroups/cgroup_trace.bt "$cgid" "$cgcmd" "$debug"
    fi
  else
    if [ -n "$out" ]; then
      bpftrace -o "$out" bpftrace/cgroups/cgroup_trace.bt "$cgid" "$debug"
    else
      bpftrace bpftrace/cgroups/cgroup_trace.bt "$cgid" "$debug"
    fi
  fi

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
