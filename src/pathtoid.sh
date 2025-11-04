#!/usr/bin/env sh
# file: pathtoid.sh
# Usage:
#   ./pathtoid.sh /sys/fs/cgroup/kubepods/burstable/pod8082188858b9552b4450a72f53513e15.slice/cri-containerd-a9fe3a952a7c5dda8bbb67f2e8270de234b11b1761bfb9db260d363925723fae.scope

# input: (container, pod (name/id), namespace)
# running: sudo crictl ps => output is containerid
# input: containerid
# running: sudo find /sys/fs/cgroup/ -type d -name "*${containerid}*" => output is cgroupid (full path)
# input: cgroupid

set -eu

# take the first input as cgroup path
path="$1"

# find numeric cgroupid for a container
stat -c %i "${path}"
