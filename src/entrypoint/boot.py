#!/usr/bin/env python3
# file: entrypoint/boot.py

import argparse
import os
import sys
import subprocess
import shutil
import time
import json



def main():
    parser = argparse.ArgumentParser(
        description="Bootstraps a tracing session for a pod/container. "
                    "Required: --container, --pod, --namespace. "
                    "Optional: --command, --output."
    )

    parser.add_argument("--container", required=True, help="Container name or ID")
    parser.add_argument("--pod", required=True, help="Pod name or ID")
    parser.add_argument("--namespace", required=True, help="Kubernetes namespace")
    parser.add_argument("--command", help="Command to execute inside the container")
    parser.add_argument("--output", default="logs", help="Folder path to export the tracing logs")

    args = parser.parse_args()
    
    container_name = args.container
    pod_name = args.pod
    namespace = args.namespace
    command = args.command
    output_path = args.output

    # prepare output directory
    if os.path.isdir(output_path):
        shutil.rmtree(output_path)
    os.makedirs(output_path, exist_ok=True)

    # print out what we are looking for
    if command:
        print(f"looking for {container_name}/{command} in {namespace}/{pod_name} ...")
    else:
        print(f"looking for {container_name} in {namespace}/{pod_name} ...")

    # print and write reference timestamps
    ref_wall = time.time()
    try:
        with open("/proc/uptime") as f:
            ref_mono = float(f.read().split()[0])
    except Exception:
        ref_mono = None

    print("use these parameters for timestamp changes:")
    print(f"\t ref wall: {ref_wall}")
    print(f"\t ref mono: {ref_mono}")

    meta_file = os.path.join(output_path, "meta.json")
    with open(meta_file, "w") as mf:
        json.dump({"ref_wall": ref_wall, "ref_mono": ref_mono}, mf, indent=2)
    print(f"Metadata saved to: {meta_file}")

    # poll for the container ID
    while True:
        print("waiting ...")
        try:
            result = subprocess.run(
                ["crictl", "ps", "--namespace", namespace],
                capture_output=True, text=True, check=True
            )
        except subprocess.CalledProcessError as exc:
            print(f"Error running crictl ps: {exc}", file=sys.stderr)
            sys.exit(1)

        containerid = None
        for line in result.stdout.splitlines()[1:]:
            parts = line.split()
            # defensive: crictl output can be variable, so require enough columns
            if len(parts) >= 11 and parts[9] == pod_name and parts[6] == container_name:
                containerid = parts[0]
                break

        if containerid:
            print(f"target container found: {container_name} => {containerid}")
            break

        time.sleep(0.5)

    # find cgroup path
    try:
        find_proc = subprocess.run(
            ["find", "/sys/fs/cgroup/", "-type", "d", "-name", f"*{containerid}*"],
            capture_output=True, text=True, check=True
        )
        path = find_proc.stdout.strip().splitlines()[0]
    except Exception:
        print("Could not find cgroup path!", file=sys.stderr)
        sys.exit(1)

    # find numeric cgroupid
    try:
        stat_proc = subprocess.run(
            ["stat", "-c", "%i", path],
            capture_output=True, text=True, check=True
        )
        cgroupid = stat_proc.stdout.strip()
    except Exception:
        print(f"Could not determine cgroupid for {path}", file=sys.stderr)
        sys.exit(1)

    print("igniting tracer")

    # call bpftrace
    log_out = os.path.join(output_path, "logs.txt")
    if command:
        tracer_args = ["bpftrace", "-o", log_out, "bpftrace/cgroup_comm_trace.bt", cgroupid, command]
    else:
        tracer_args = ["bpftrace", "-o", log_out, "bpftrace/cgroup_trace.bt", cgroupid]

    rc = subprocess.call(tracer_args)
    sys.exit(rc)

if __name__ == "__main__":
    main()
