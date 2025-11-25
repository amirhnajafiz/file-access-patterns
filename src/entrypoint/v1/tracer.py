# file: src/entrypoint/tracer.py
import subprocess
import sys



def termination_hook(signum, _):
    if signum != None:
        print(f"\nReceived signal {signum}, shutting down safely ...")


def start_new_tracer(bt_command: str) -> int:
    rc = subprocess.call(bt_command)
    if rc != 0:
        print(f"bpftrace exited with code {rc}", file=sys.stderr)
    termination_hook(None, None)
    return rc
