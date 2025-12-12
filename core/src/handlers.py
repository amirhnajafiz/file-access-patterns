import os

from src.files import get_tracing_scripts
from src.tracer import Tracer, RotateTracer
from src.utils import ensure_script


def handle_execute(output_dir: str, execute: str) -> list[Tracer]:
    """Handle the execute command.

    running: bpftrace -o output -c "command" bpftrace/execute/<tracer>.bt

    :param output_dir: tracing output directory
    :param execute: the command to execute
    :return: list of tracing scripts
    """
    tracers = []

    for tname, tpath in get_tracing_scripts("bpftrace/execute").items():
        ensure_script(tpath)

        tracer = Tracer(tname, tpath)
        tracer.with_options(["-o", os.path.join(output_dir, tname + "_logs.txt")])
        tracer.with_options(["-c", execute])

        tracers.append(tracer)

    return tracers


def handle_pid(output_dir: str, pid: str) -> list[Tracer]:
    """Handle the pid tracing.

    running: bpftrace -o output bpftrace/pid/<tracer>.bt <pid>

    :param output_dir: tracing output directory
    :param pid: the pid to trace
    :return: list of tracing scripts
    """
    tracers = []

    for tname, tpath in get_tracing_scripts("bpftrace/pid").items():
        ensure_script(tpath)

        tracer = Tracer(tname, tpath)
        tracer.with_options(["-o", os.path.join(output_dir, tname + "_logs.txt")])
        tracer.with_args([pid])

        tracers.append(tracer)

    return tracers


def handle_command(output_dir: str, command: str) -> list[Tracer]:
    """Handle the command tracing.

    running: bpftrace -o output bpftrace/command/<tracer>.bt <command>

    :param output_dir: tracing output directory
    :param command: the command to trace
    :return: list of tracing scripts
    """
    tracers = []

    for tname, tpath in get_tracing_scripts("bpftrace/command").items():
        ensure_script(tpath)

        tracer = Tracer(tname, tpath)
        tracer.with_options(["-o", os.path.join(output_dir, tname + "_logs.txt")])
        tracer.with_args([command])

        tracers.append(tracer)

    return tracers


def handle_cgroup_and_command(
    output_dir: str, cgid: str, filter_command: str
) -> list[Tracer]:
    """Handle the cgroup and command tracing.

    running: bpftrace -o output bpftrace/cgroup_and_command/<tracer>.bt <cgroup> <command>

    :param output_dir: tracing output directory
    :param cgid: the cgroup to trace
    :param filter_command: the command to filter
    :return: list of tracing scripts
    """
    tracers = []

    for tname, tpath in get_tracing_scripts("bpftrace/cgroup_and_command").items():
        ensure_script(tpath)

        tracer = Tracer(tname, tpath)
        tracer.with_options(["-o", os.path.join(output_dir, tname + "_logs.txt")])
        tracer.with_args([cgid, filter_command])

        tracers.append(tracer)

    return tracers


def handle_cgroup(output_dir: str, cgid: str) -> list[Tracer]:
    """Handle the cgroup tracing.

    running: bpftrace -o output bpftrace/cgroup/<tracer>.bt <cgroup>

    :param output_dir: tracing output directory
    :param cgid: the cgroup to trace
    :return: list of tracing scripts
    """
    tracers = []

    for tname, tpath in get_tracing_scripts("bpftrace/cgroup").items():
        ensure_script(tpath)

        tracer = Tracer(tname, tpath)
        tracer = RotateTracer(tname, tpath, output_dir, rotate_size=1*1024*1024)
        #tracer.with_options(["-o", os.path.join(output_dir, tname + "_logs.txt")])
        tracer.with_args([cgid])

        tracers.append(tracer)

    return tracers
