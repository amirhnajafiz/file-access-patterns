#!/usr/bin/env sh
# file: tests/cgroups.sh

set -eu

directory="bpftrace/cgroups"

# test `tracings` scripts
sudo bpftrace -dd "${directory}/cgroup_trace.bt" 1
exit_status=$?
if [ "$exit_status" -ne 0 ]; then
    echo "cgroup_trace.bt failed"
fi

sudo bpftrace -dd -c "ls" "${directory}/cgroup_comm_trace.bt" 1 tmp
exit_status=$?
if [ "$exit_status" -ne 0 ]; then
    echo "cgroup_comm_trace.bt failed"
fi

echo "passed all tests."
