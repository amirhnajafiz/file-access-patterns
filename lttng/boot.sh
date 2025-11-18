#!/usr/bin/env sh
# file: entrypoint/boot.sh

# Usage:
#   ./boot.sh --container <CONTAINER> --pod <POD> --namespace <NAMESPACE> [--command <COMMAND>]

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
EOF
}

# default values
container_name=""
pod_name=""
namespace=""
command=""

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
    containerid=$(crictl ps --namespace "${namespace}" | awk -v pod="${pod_name}" -v cname="${container_name}" 'NR > 1 && $10 == pod && $7 == cname { print $1}')

    if [ -n "$containerid" ]; then
        echo "target container found: ${container_name} => ${containerid}"
        break
    fi

    sleep 0.5
done

# input: containerid
# running: sudo find /sys/fs/cgroup/ -type d -name "*${containerid}*" => output is cgroupid (full path)
path=$(find /sys/fs/cgroup/ -type d -name "*${containerid}*")

# list all pids for the cgroup
pids=$(cat "${path}/cgroup.procs")

echo "PIDs in container (${containerid}) cgroup:"
echo "${pids}"

# select the lowest (oldest) PID in the cgroup as the likely init process
init_pid=$(echo "${pids}" | sort -n | head -1)

echo "Likely container init PID: ${init_pid}"

# get the pid namespace inode using lsns
pid_ns=$(lsns -n -t pid -o NS -p "${init_pid}" | awk 'NR==1 {print $1}')

echo "pid namespace inode: ${pid_ns}"

# input: cgroup path
# find numeric cgroupid for a container
cgroupid=$(stat -c %i "${path}")
echo "${cgroupid}"

echo "igniting tracer"
