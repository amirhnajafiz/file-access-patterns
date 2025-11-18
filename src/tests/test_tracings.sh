#!/usr/bin/env sh
# file: tests/test_tracings.sh

set -eu

directory="bpftrace"

# test `tracings` scripts
bpftrace -dd "${directory}/comm_trace.bt" tmp 1
exit_status=$?
if [ "$exit_status" -ne 0 ]; then
    echo "comm_trace.bt failed"
fi

bpftrace -dd -c "ls" "${directory}/cmd_trace.bt" 1
exit_status=$?
if [ "$exit_status" -ne 0 ]; then
    echo "cmd_trace.bt failed"
fi

bpftrace -dd "${directory}/pid_trace.bt" 1 1
exit_status=$?
if [ "$exit_status" -ne 0 ]; then
    echo "pid_trace.bt failed"
fi

echo "passed all tests."
