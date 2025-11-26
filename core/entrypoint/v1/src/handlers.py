import os

from files import get_tracing_scripts
from tracer import Tracer
from utils import ensure_script


def handle_execute(output_dir: str, execute: str) -> list[Tracer]:
    tracers = []

    for tname, tpath in get_tracing_scripts("bpftrace/execute").items():
        ensure_script(tpath)

        tracer = Tracer(tname, tpath)
        tracer.with_options(["-o", os.path.join(output_dir, tname + ".txt")])
        tracer.with_options(["-c", execute])

        tracers.append([tracer])

    return tracers

def handle_pid(output_dir: str, pid: str) -> list[Tracer]:
    tracers = []

    for tname, tpath in get_tracing_scripts("bpftrace/pid").items():
        ensure_script(tpath)

        tracer = Tracer(tname, tpath)
        tracer.with_options(["-o", os.path.join(output_dir, tname + ".txt")])
        tracer.with_args([pid])

        tracers.append(tracer)

    return tracers

def handle_command(output_dir: str, command: str) -> list[Tracer]:
    tracers = []

    for tname, tpath in get_tracing_scripts("bpftrace/command").items():
        ensure_script(tpath)

        tracer = Tracer(tname, tpath)
        tracer.with_options(["-o", os.path.join(output_dir, tname + ".txt")])
        tracer.with_args([command])

        tracers.append(tracer)

    return tracers

def handle_cgroup_and_command(output_dir: str, cgid: str, filter_command: str) -> list[Tracer]:
    tracers = []

    for tname, tpath in get_tracing_scripts("bpftrace/cgroup_and_command").items():
        ensure_script(tpath)

        tracer = Tracer(tname, tpath)
        tracer.with_options(["-o", os.path.join(output_dir, tname + ".txt")])
        tracer.with_args([cgid, filter_command])

        tracers.append(tracer)

    return tracers

def handle_cgroup(output_dir: str, cgid: str) -> list[Tracer]:
    tracers = []

    for tname, tpath in get_tracing_scripts("bpftrace/cgroup").items():
        ensure_script(tpath)

        tracer = Tracer(tname, tpath)
        tracer.with_options(["-o", os.path.join(output_dir, tname + ".txt")])
        tracer.with_args([cgid])

        tracers.append(tracer)

    return tracers
