# file: src/entrypoint/app.py
import argparse
import json
import os
import shutil
import signal
import sys
import threading
import time

from tracer import termination_hook, start_new_tracer



def must_support_bpftrace():
    # check if bpftrace is available
    if shutil.which("bpftrace") is None:
        print("Error: bpftrace not found in PATH. Please install bpftrace.", file=sys.stderr)
        sys.exit(3)

def init_output(out: str):
    # prepare output directory
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out, exist_ok=True)

def export_reference_timestamps(out: str):
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

def get_tracers(dir_path: str) -> list[str]:
    pass

def process(args: argparse.Namespace):
    init_output(args.out)
    export_reference_timestamps(args.out)

    threads = []
    for tracer in get_tracers(args.out):
        t = threading.Thread(target=start_new_tracer, args=(tracer))
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()

def main():
    parser = argparse.ArgumentParser(
        description="File Access Patterns (aka FLAP) tracing tool. Enabling I/O tracing for processes."
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-ex", "--execute", help="execute a command and trace it")
    group.add_argument("-p", "--pid", help="trace an existing process by PID")
    group.add_argument("-c", "--command", help="trace all processes by their command name")
    group.add_argument("-cg", "--cgroup", help="trace processes by cgroup ID")

    parser.add_argument("-cmd", help="Filter based on a command in cgroup tracing (only works with -cg|--cgroup)")
    parser.add_argument("-o", "--out", default="logs", help="Folder path to export the tracing logs (default: logs)")
    parser.add_argument("-mxsl", "--max_str_len", default="64", help="bpf MAX_STRLEN in bytes (default: 64)")

    args = parser.parse_args()
    os.environ['BPFTRACE_MAX_STRLEN'] = args.max_str

    must_support_bpftrace()
    process(args=args)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, termination_hook)
    signal.signal(signal.SIGTERM, termination_hook)
    main()
