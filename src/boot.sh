#!/usr/bin/env sh
# file: boot.sh

# Usage:
#   ./boot.sh <CONTAINER> <POD> <NAMESPACE>

set -eu

# input: (container, pod (name/id), namespace)
cnm="$1"
pod="$2"
nsp="$3"

# running: sudo crictl ps => output is containerid
containerid=$(sudo crictl ps --namespace "${nsp}" | awk -v pod="${pod}" -v cname="${cnm}" 'NR > 1 && $10 == pod && $7 == cname { print $1}')

# input: containerid
# running: sudo find /sys/fs/cgroup/ -type d -name "*${containerid}*" => output is cgroupid (full path)
path=$(sudo find /sys/fs/cgroup/ -type d -name "*${containerid}*")

# input: cgroup path
# find numeric cgroupid for a container
cgroupid=$(stat -c %i "${path}")

# call the tracer by cgroup
sudo bpftrace -o /tmp/logs.txt scripts/ctrace_cgid.bt "${cgroupid}"
