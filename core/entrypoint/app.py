import argparse
import logging
import os
import sys

import src.handlers as hd
from src.files import create_dir
from src.timestamp import export_reference_timestamps
from src.utils import must_support_bpftrace


def process(args: argparse.Namespace):
    # list of tracers (type: src/tracer/Tracer)
    tracers = []

    # call handler based on user input to get the tracers
    if args.execute:
        tracers = hd.handle_execute(args.out, args.execute)
    elif args.pid:
        tracers = hd.handle_pid(args.out, args.pid)
    elif args.command:
        tracers = hd.handle_command(args.out, args.command)
    elif args.cgroup and args.filter_command:
        tracers = hd.handle_cgroup_and_command(args.out, args.cgroup, args.filter_command)
    elif args.cgroup:
        tracers = hd.handle_cgroup(args.out, args.cgroup)
    else:
        logging.error("nothing provided")
        sys.exit(1)

    # prepare tracing requirements
    create_dir(args.out)
    export_reference_timestamps(args.out)

    # loop over tracers and start
    for tracer in tracers:
        tracer.start()

    # wait for all tracers
    for tracer in tracers:
        tracer.wait()


def init_vars(args: argparse.Namespace):
    os.environ["BPFTRACE_MAX_STRLEN"] = args.max_str_len
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )


def main():
    # create an argument parser
    parser = argparse.ArgumentParser(
        description="File Access Patterns (aka FLAP) tracing tool. Enabling I/O tracing for processes."
    )

    # required arguments
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-ex", "--execute", help="execute a command and trace it using its PID"
    )
    group.add_argument(
        "-p",
        "--pid",
        help="trace an existing process using its PID (must be in running state)",
    )
    group.add_argument(
        "-c", "--command", help="trace all processes by their command name"
    )
    group.add_argument(
        "-cg",
        "--cgroup",
        help="trace processes by their Cgroup ID (must be a valid cgroup)",
    )

    # optional arguments
    parser.add_argument(
        "-fc",
        "--filter_command",
        help="Filter based on a command in cgroup tracing (only works with -cg|--cgroup)",
    )
    parser.add_argument(
        "-o",
        "--out",
        default="logs",
        help="Folder path to export the tracing logs (default: logs)",
    )
    parser.add_argument(
        "-mxsl",
        "--max_str_len",
        default="64",
        help="bpf MAX_STRLEN in bytes (default: 64)",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action='store_true',
        help="Enable debug mode (print debug messages)"
    )

    # parse the arguments
    args = parser.parse_args()

    # check the requirements
    must_support_bpftrace()

    # init variables
    init_vars(args=args)

    # start processing the input
    process(args=args)


if __name__ == "__main__":
    main()
