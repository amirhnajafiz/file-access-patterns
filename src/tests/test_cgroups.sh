#!/usr/bin/env sh
# file: tests/test_cgroups.sh

set -eu

directory="bpftrace/cgroups"

# test `tracings` scripts
bpftrace -dd "${directory}/cgroup_trace.bt" 1 0
exit_status=$?
if [ "$exit_status" -ne 0 ]; then
    echo "cgroup_trace.bt failed"
fi

bpftrace -dd -c "ls" "${directory}/cgroup_comm_trace.bt" 1 tmp 1
exit_status=$?
if [ "$exit_status" -ne 0 ]; then
    echo "cgroup_comm_trace.bt failed"
fi

echo "passed all tests."
