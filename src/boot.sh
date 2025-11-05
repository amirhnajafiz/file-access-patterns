#!/usr/bin/env sh
# file: boot.sh

# Usage:
#   ./boot.sh <CONTAINER> <POD> <NAMESPACE>

set -eu

# input: (container, pod (name/id), namespace, command)
container_name="$1"
pod_name="$2"
namespace="$3"

if [ "$#" -eq 3]; then
    command="$4"
else
    command=""
fi

if [ -n "$command"]; then
    echo "looking for ${container_name}/${command} in ${namespace}/${pod_name} ..."
else
    echo "looking for ${container_name} in ${namespace}/${pod_name} ..."
fi

# running: sudo crictl ps => output is containerid
while true; do
    echo "waiting ..."
    containerid=$(sudo crictl ps --namespace "${namespace}" | awk -v pod="${pod_name}" -v cname="${container_name}" 'NR > 1 && $10 == pod && $7 == cname { print $1}')

    if [ -n "$containerid" ]; then
        echo "target found: ${containerid}"
        break
    fi

    sleep 0.5
done

# input: containerid
# running: sudo find /sys/fs/cgroup/ -type d -name "*${containerid}*" => output is cgroupid (full path)
path=$(sudo find /sys/fs/cgroup/ -type d -name "*${containerid}*")

# input: cgroup path
# find numeric cgroupid for a container
cgroupid=$(stat -c %i "${path}")

echo "igniting tracer"

# call the tracer by cgroup
if [ -n "$command"]; then
    sudo bpftrace scripts/cntrace_cgid.bt "${cgroupid}" "${command}"
else
    sudo bpftrace scripts/ctrace_cgid.bt "${cgroupid}"
fi
