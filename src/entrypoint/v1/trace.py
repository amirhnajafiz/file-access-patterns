#!/usr/bin/env python3
# file: entrypoint/v1/trace.py

import os
import sys
import subprocess
import signal
import threading
import time
from typing import List



# Configurable timeouts (seconds)
GRACE_PERIOD_SIGINT = 5.0    # wait after SIGINT
GRACE_PERIOD_SIGTERM = 3.0   # wait after SIGTERM
FORCE_KILL_TIMEOUT = 2.0     # final wait after SIGKILL (should be short)

shutdown_in_progress = threading.Event()


def start_bpftrace_process(script_path: str) -> subprocess.Popen:
    """
    Start a bpftrace script as a child process in its own process group.
    We forward stdout/stderr so user can see output live.
    """
    if not os.path.exists(script_path):
        raise FileNotFoundError(f"Script not found: {script_path}")

    # preexec_fn=os.setsid makes the child the leader of a new process group
    proc = subprocess.Popen(
        ["bpftrace", script_path],
        stdout=sys.stdout,
        stderr=sys.stderr,
        stdin=subprocess.DEVNULL,
        preexec_fn=os.setsid,
        close_fds=True,
    )
    return proc


def _kill_process_group(pg: int, sig: int):
    try:
        os.killpg(pg, sig)
    except ProcessLookupError:
        # already gone
        pass
    except PermissionError:
        print(f"PermissionError when sending {sig} to pg {pg}", file=sys.stderr)


def graceful_shutdown(procs: List[subprocess.Popen]):
    """
    Attempt a graceful shutdown:
      1) send SIGINT (graceful)
      2) wait GRACE_PERIOD_SIGINT
      3) send SIGTERM
      4) wait GRACE_PERIOD_SIGTERM
      5) send SIGKILL
    """
    if shutdown_in_progress.is_set():
        return
    shutdown_in_progress.set()
    print("\n[master] Shutdown initiated...")

    # Filter out processes that are already finished
    alive_procs = [p for p in procs if p.poll() is None]
    if not alive_procs:
        print("[master] No child processes are running.")
        return

    # 1) Send SIGINT to each process group
    print("[master] Sending SIGINT to child process groups...")
    for p in alive_procs:
        try:
            pg = os.getpgid(p.pid)
            _kill_process_group(pg, signal.SIGINT)
        except Exception as e:
            print(f"[master] Warning: failed to signal pg for pid {p.pid}: {e}", file=sys.stderr)

    # Wait for them to exit
    _wait_for_procs(alive_procs, timeout=GRACE_PERIOD_SIGINT)

    # Recompute alive
    alive_procs = [p for p in procs if p.poll() is None]
    if not alive_procs:
        print("[master] All children exited after SIGINT.")
        return

    # 2) Send SIGTERM
    print("[master] Sending SIGTERM to child process groups...")
    for p in alive_procs:
        try:
            pg = os.getpgid(p.pid)
            _kill_process_group(pg, signal.SIGTERM)
        except Exception as e:
            print(f"[master] Warning: failed to SIGTERM pg for pid {p.pid}: {e}", file=sys.stderr)

    _wait_for_procs(alive_procs, timeout=GRACE_PERIOD_SIGTERM)

    # Recompute alive
    alive_procs = [p for p in procs if p.poll() is None]
    if not alive_procs:
        print("[master] All children exited after SIGTERM.")
        return

    # 3) Force kill
    print("[master] Force killing remaining child process groups (SIGKILL)...")
    for p in alive_procs:
        try:
            pg = os.getpgid(p.pid)
            _kill_process_group(pg, signal.SIGKILL)
        except Exception as e:
            print(f"[master] Warning: failed to SIGKILL pg for pid {p.pid}: {e}", file=sys.stderr)

    _wait_for_procs(alive_procs, timeout=FORCE_KILL_TIMEOUT)
    still_alive = [p for p in procs if p.poll() is None]
    if still_alive:
        print("[master] Some children are still alive after SIGKILL (unexpected).", file=sys.stderr)
    else:
        print("[master] Shutdown complete. All child processes terminated.")


def _wait_for_procs(procs: List[subprocess.Popen], timeout: float):
    """
    Wait up to `timeout` seconds for all procs to exit. Polls periodically.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        if all(p.poll() is not None for p in procs):
            return
        time.sleep(0.1)


def _signal_handler(signum, frame, procs: List[subprocess.Popen]):
    print(f"\n[master] Received signal {signum}; starting shutdown handler.")
    # run the graceful shutdown in a separate thread so the signal handler stays minimal
    t = threading.Thread(target=graceful_shutdown, args=(procs,), daemon=True)
    t.start()


def run_scripts_and_wait(script_paths: List[str]) -> int:
    """
    Start scripts, install signal handlers, and wait for them to finish or for termination.
    Returns an exit code.
    """
    procs: List[subprocess.Popen] = []
    try:
        for path in script_paths:
            print(f"[master] Starting: {path}")
            p = start_bpftrace_process(path)
            print(f"[master] Started PID {p.pid} for {path}")
            procs.append(p)
    except Exception as e:
        print(f"[master] Failed to start processes: {e}", file=sys.stderr)
        # try best-effort cleanup
        graceful_shutdown(procs)
        return 2

    # Install signal handlers; handlers will spawn a thread to perform shutdown
    signal.signal(signal.SIGINT, lambda s, f: _signal_handler(s, f, procs))
    signal.signal(signal.SIGTERM, lambda s, f: _signal_handler(s, f, procs))

    # Main wait loop: return when all children exit or shutdown flag set and children gone
    try:
        while True:
            # If shutdown requested, perform shutdown (if not already in progress)
            if shutdown_in_progress.is_set():
                # Ensure shutdown sequence ran (it may have started in handler thread)
                graceful_shutdown(procs)
                break

            # Check if all procs finished normally
            all_done = all(p.poll() is not None for p in procs)
            if all_done:
                print("[master] All child processes have completed.")
                break

            time.sleep(0.2)

    except KeyboardInterrupt:
        # In case Ctrl+C falls through
        print("\n[master] KeyboardInterrupt observed in main thread. Initiating shutdown.")
        graceful_shutdown(procs)

    # Return an exit code: 0 if all children exited zero, else first non-zero child exit code or 1
    exit_codes = [p.returncode for p in procs if p.returncode is not None]
    if not exit_codes:
        return 0
    for code in exit_codes:
        if code != 0:
            return code
    return 0


def main(argv):
    if len(argv) >= 2:
        scripts = argv[1:]
    else:
        # Example: replace with your real script paths
        scripts = [
            "/path/to/script1.bt",
            "/path/to/script2.bt",
            "/path/to/script3.bt",
        ]
        print("[master] No scripts provided on command-line; using example paths (edit the script).")

    # Basic check
    for p in scripts:
        if not os.path.exists(p):
            print(f"[master] Warning: script not found: {p}", file=sys.stderr)

    rc = run_scripts_and_wait(scripts)
    print(f"[master] Exiting with code {rc}")
    sys.exit(rc)


if __name__ == "__main__":
    main(sys.argv)
