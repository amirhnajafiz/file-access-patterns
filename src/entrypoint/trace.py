#!/usr/bin/env python3
# file: entrypoint/trace.py

import argparse
import os
import sys
import subprocess
import shutil
import time
import json
import signal



def handle_shutdown(signum, _):
    print(f"\nReceived signal {signum}, shutting down safely ...")
    sys.exit(0)

# register handlers for SIGINT (Ctrl+C) and SIGTERM
signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)

def ensure_script(path):
    if not os.path.isfile(path):
        print(f"Error: required script '{path}' not found.", file=sys.stderr)
        sys.exit(4)

def main():
    parser = argparse.ArgumentParser(
        description="Traces all file access events of a command and its sub-processes, "
                    "outputs the total bytes read/written and access times."
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-c", "--cmd", help="trace a command and its subprocesses (bpftrace/cmd_trace.bt)")
    group.add_argument("-p", "--pid", help="trace an existing process by PID (bpftrace/pid_trace.bt)")
    group.add_argument("-n", "--name", help="trace all processes by name (bpftrace/comm_trace.bt)")
    group.add_argument("-cg", "--cgid", help="trace processes by cgroup ID (bpftrace/cgroup_trace.bt)")

    parser.add_argument("-cgcmd", help="Filter based on a command in cgroup tracing (only works with -cg)")
    parser.add_argument("-o", "--out", default="logs", help="Folder path to export the tracing logs (default: logs)")

    args = parser.parse_args()

    # check if bpftrace is available
    if shutil.which("bpftrace") is None:
        print("Error: bpftrace not found in PATH. Please install bpftrace.", file=sys.stderr)
        sys.exit(3)

    # prepare output directory
    out = args.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out, exist_ok=True)

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

    meta_file = os.path.join(out, "meta.json")
    with open(meta_file, "w") as mf:
        json.dump({"ref_wall": ref_wall, "ref_mono": ref_mono}, mf, indent=2)
    print(f"Metadata saved to: {meta_file}")

    # determine which script to run
    bt_args = None
    if args.cmd:
        script = "bpftrace/tracings/cmd_trace.bt"
        ensure_script(script)
        bt_args = ["bpftrace", "-o", f"{out}/logs.txt", "-c", args.cmd, script]
    elif args.pid:
        script = "bpftrace/tracings/pid_trace.bt"
        ensure_script(script)

        # Validate pid is numeric
        if not args.pid.isdigit():
            print("Error: pid must be a positive integer.", file=sys.stderr)
            sys.exit(2)

        bt_args = ["bpftrace", "-o", f"{out}/logs.txt", script, args.pid]
    elif args.name:
        script = "bpftrace/tracings/comm_trace.bt"
        ensure_script(script)
        bt_args = ["bpftrace", "-o", f"{out}/logs.txt", script, args.name]
    elif args.cgid:
        script = "bpftrace/cgroups/cgroup_trace.bt"
        ensure_script(script)

        # validate cgid is numeric
        if not args.cgid.isdigit():
            print("Error: cgroupid must be a positive integer.", file=sys.stderr)
            sys.exit(2)

        if args.cgcmd:
            bt_args = ["bpftrace", "-o", f"{out}/logs.txt", script, args.cgid, args.cgcmd]
        else:
            bt_args = ["bpftrace", "-o", f"{out}/logs.txt", script, args.cgid]
    else:
        print("Error: either -c <command>, -p <pid>, -cg <cgroupid> or -n <name> must be provided.", file=sys.stderr)

    # run bpftrace if arguments are set
    if bt_args:
        rc = subprocess.call(bt_args)
        if rc != 0:
            print(f"bpftrace exited with code {rc}", file=sys.stderr)
        sys.exit(rc)

if __name__ == "__main__":
    main()
