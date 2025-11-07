#!/usr/bin/env sh
# file: boot.sh

# Usage:
#   ./boot.sh --container <CONTAINER> --pod <POD> --namespace <NAMESPACE> [--command <COMMAND>] [--debug]

set -eu

print_usage() {
  cat <<EOF
Usage:
  $0 --container <CONTAINER> --pod <POD> --namespace <NAMESPACE> [--command <COMMAND>]

Required flags:
  --container   Container name or ID
  --pod         Pod name or ID
  --namespace   Kubernetes namespace

Optional flags:
  --command     Command to execute inside the container
  --debug       Display debug lines in bpftrace program
EOF
}

# default values
container_name=""
pod_name=""
namespace=""
command=""
debug=0

# Parse arguments
while [ $# -gt 0 ]; do
  case "$1" in
    --container)
      container_name="$2"
      shift 2
      ;;
    --pod)
      pod_name="$2"
      shift 2
      ;;
    --namespace)
      namespace="$2"
      shift 2
      ;;
    --command)
      command="$2"
      shift 2
      ;;
    --debug)
      debug=1
      shift 2
      ;;
    -h|--help)
      print_usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      print_usage
      exit 1
      ;;
  esac
done

# validate required flags
if [ -z "$container_name" ] || [ -z "$pod_name" ] || [ -z "$namespace" ]; then
  echo "Error: --container, --pod, and --namespace are required."
  print_usage
  exit 1
fi

if [ -n "$command" ]; then
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
if [ -n "$command" ]; then
    sudo bpftrace bpftrace/cgroups/cgroup_comm_trace.bt "${cgroupid}" "${command}" "${debug}
else
    sudo bpftrace bpftrace/cgroups/cgroup_trace.bt "${cgroupid}" "${debug}"
fi
