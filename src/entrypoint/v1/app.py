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
    """check if bpftrace is supported."""
    if shutil.which("bpftrace") is None:
        print("Error: bpftrace not found in PATH. Please install bpftrace.", file=sys.stderr)
        sys.exit(3)


def init_output(out: str):
    """prepare output directory."""
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out, exist_ok=True)


def export_reference_timestamps(out: str):
    """print and write reference timestamps."""
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


def get_tracing_scripts(dir_path: str) -> dict[str: str]:
    """return the path of tracing scripts based on input directory path."""
    return {
        "meta_logs": os.path.join(dir_path, "meta_trace.bt"),
        "io_logs": os.path.join(dir_path, "io_trace.bt"),
        "event_logs": os.path.join(dir_path, "events_trace.bt")
    }


def ensure_script(path):
    """make sure the target script exists."""
    if not os.path.isfile(path):
        print(f"Error: required script '{path}' not found.", file=sys.stderr)
        sys.exit(4)


def process(args: argparse.Namespace):
    output_dir_path = args.out  # output directory
    tracer_commands = []        # tracer commands

    if args.execute:
        for tracer_name, tracer_path in get_tracing_scripts("bpftrace/execute").items():
            ensure_script(tracer_path)

            bt_command = [
                "bpftrace",
                "-o",
                f"{output_dir_path}/{tracer_name}.txt",
                "-c",
                args.execute,
                tracer_path
            ]

            tracer_commands.append(' '.join(bt_command))
    elif args.pid:
        for tracer_name, tracer_path in get_tracing_scripts("bpftrace/pid").items():
            ensure_script(tracer_path)

            bt_command = [
                "bpftrace",
                "-o",
                f"{output_dir_path}/{tracer_name}.txt",
                tracer_path,
                args.pid
            ]

            tracer_commands.append(' '.join(bt_command))
    elif args.command:
        for tracer_name, tracer_path in get_tracing_scripts("bpftrace/command").items():
            ensure_script(tracer_path)

            bt_command = [
                "bpftrace",
                "-o",
                f"{output_dir_path}/{tracer_name}.txt",
                tracer_path,
                args.command
            ]

            tracer_commands.append(' '.join(bt_command))
    elif args.cgid and args.filter_command:
        for tracer_name, tracer_path in get_tracing_scripts("bpftrace/cgroup_and_command").items():
            ensure_script(tracer_path)

            bt_command = [
                "bpftrace",
                "-o",
                f"{output_dir_path}/{tracer_name}.txt",
                tracer_path,
                args.cgid,
                args.filter_command
            ]

            tracer_commands.append(' '.join(bt_command))
    elif args.cgid:
        for tracer_name, tracer_path in get_tracing_scripts("bpftrace/cgroup").items():
            ensure_script(tracer_path)

            bt_command = [
                "bpftrace",
                "-o",
                f"{output_dir_path}/{tracer_name}.txt",
                tracer_path,
                args.cgid
            ]

            tracer_commands.append(' '.join(bt_command))
    else:
        print("Error: nothing provided.", file=sys.stderr)
        sys.exit(1)

    # prepare tracing requirements
    init_output(args.out)
    export_reference_timestamps(args.out)

    # loop over the tracer commands and start a new tracer for each command
    threads = []
    for tcmd in tracer_commands:
        # start tracer
        t = threading.Thread(target=start_new_tracer, args=(tcmd))
        t.start()
        threads.append(t)
    
    # wait for all tracers
    for t in threads:
        t.join()


def main():
    # create a parser
    parser = argparse.ArgumentParser(
        description="File Access Patterns (aka FLAP) tracing tool. Enabling I/O tracing for processes."
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-ex", "--execute", help="execute a command and trace it")
    group.add_argument("-p", "--pid", help="trace an existing process by PID")
    group.add_argument("-c", "--command", help="trace all processes by their command name")
    group.add_argument("-cg", "--cgroup", help="trace processes by cgroup ID")

    parser.add_argument("-fc", "--filter_command", help="Filter based on a command in cgroup tracing (only works with -cg|--cgroup)")
    parser.add_argument("-o", "--out", default="logs", help="Folder path to export the tracing logs (default: logs)")
    parser.add_argument("-mxsl", "--max_str_len", default="64", help="bpf MAX_STRLEN in bytes (default: 64)")

    args = parser.parse_args()

    # set the env variables
    os.environ['BPFTRACE_MAX_STRLEN'] = args.max_str

    # check the requirements
    must_support_bpftrace()

    # set the termination hooks
    signal.signal(signal.SIGINT, termination_hook)
    signal.signal(signal.SIGTERM, termination_hook)

    # start processing the input
    process(args=args)

if __name__ == "__main__":
    main()
