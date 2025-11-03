#!/usr/bin/env sh
# file: pathtoid.sh
# Usage:
#   ./pathtoid.sh /sys/fs/cgroup/kubepods/burstable/pod8082188858b9552b4450a72f53513e15.slice/cri-containerd-a9fe3a952a7c5dda8bbb67f2e8270de234b11b1761bfb9db260d363925723fae.scope

set -eu

path="$1"

# find numeric cgroupid for a container or process
bpftrace -e "printf(\"%llu\n\", cgroupid(\"${path}\"));"
