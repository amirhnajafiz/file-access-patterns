import logging
import subprocess
import threading
import time
import os


class Tracer:
    """Class tracer is for running tracing processes based on tracing scripts and commands."""

    def __init__(self, tid: str, script: str, termination_timeout: int = 2):
        """Tracer constructor.

        :param tid: the tracer id for debugging
        :param script: the bpftrace script to run
        :param termination_timeout: tracer termination timeout in seconds
        """
        self.__tid = tid  # tracer id
        self.__options = []  # bpftrace options
        self.__args = []  # bpftrace input arguments
        self.__script = script  # bpftrace script
        self.__tto = termination_timeout

    def with_options(self, options: list[str]):
        """
        Add options to the tracer.

        :param options: a list of options to append the current options
        """
        self.__options += options

    def with_args(self, args: list[str]):
        """
        Add args to the tracer.

        :param args: a list of args to append the current args
        """
        self.__args += args

    def __start_tracer(self):
        """Start tracer in a new process and wait until its over or the stop event is received."""
        # create the bpftrace command
        bt_command = ["bpftrace"] + self.__options + [self.__script] + self.__args

        logging.debug(
            "[{}] starting tracer: {}".format(self.__tid, " ".join(bt_command))
        )

        try:
            # run a new process
            proc = subprocess.Popen(bt_command)

            while proc.poll() is None:
                if self.__stop_event.is_set():
                    logging.debug(f"[{self.__tid}] stopping tracer")
                    proc.terminate()
                    try:
                        logging.debug(f"[{self.__tid}] waiting for {self.__tto}s")
                        proc.wait(timeout=self.__tto)
                    except subprocess.TimeoutExpired:
                        logging.debug(f"[{self.__tid}] killing tracer")
                        proc.kill()
                    return
                time.sleep(0.2)
        except Exception as e:
            logging.error(f"[{self.__tid}] failed: {e}")
        finally:
            logging.debug(f"[{self.__tid}]  exiting tracer")

    def start(self):
        """Start a tracer by calling the __start_tracer in a thread."""
        self.__stop_event = threading.Event()
        self.__t = threading.Thread(target=self.__start_tracer, args=(), daemon=True)
        self.__t.start()

    def stop(self):
        """Stop the tracer by terminating its process and thread."""
        self.__stop_event.set()
        self.__t.join()

    def wait(self):
        """Wait for the tracing process to finish."""
        self.__t.join()

    def name(self) -> str:
        """Get the name of the tracer."""
        return self.__tid


class RotateTracer:
    """Tracer runs bpftrace in a separate thread with output log rotation."""

    def __init__(
        self,
        tid: str,
        script: str,
        output_dir: str,
        termination_timeout: int = 2,
        rotate_size=100 * 1024 * 1024,
    ):
        self.__tid = tid
        self.__script = script
        self.__output_dir = output_dir
        self.__tto = termination_timeout
        self.__rotate_size = rotate_size

        self.__options = []
        self.__args = []

        self.__stop_event = None
        self.__t = None

        # rotation state
        self.__file_index = 0
        self.__current_size = 0
        self.__f = None

    # ----------------------------------------------------------------------
    # API (same as your original)
    # ----------------------------------------------------------------------

    def with_options(self, options: list[str]):
        self.__options += options

    def with_args(self, args: list[str]):
        self.__args += args

    def name(self) -> str:
        return self.__tid

    def start(self):
        """Start the tracing thread."""
        self.__stop_event = threading.Event()
        self.__t = threading.Thread(target=self.__start_tracer, daemon=True)
        self.__t.start()

    def stop(self):
        """Stop the tracer."""
        if self.__stop_event:
            self.__stop_event.set()
        if self.__t:
            self.__t.join()

    def wait(self):
        """Wait until tracer thread exits."""
        if self.__t:
            self.__t.join()

    # ----------------------------------------------------------------------
    # Internal helpers
    # ----------------------------------------------------------------------

    def __open_new_file(self):
        """Rotate output file."""
        if self.__f:
            self.__f.close()

        filename = os.path.join(self.__output_dir, f"trace_{self.__tid}_{self.__file_index}.log")
        logging.info(f"[{self.__tid}] rotating to {filename}")

        self.__f = open(filename, "w", buffering=1)  # line-buffered
        self.__current_size = 0
        self.__file_index += 1

    def __write_line(self, line: str):
        data = line.encode()
        if self.__current_size + len(data) > self.__rotate_size:
            self.__open_new_file()

        self.__f.write(line)
        self.__current_size += len(data)

    # ----------------------------------------------------------------------
    # Main tracer logic
    # ----------------------------------------------------------------------

    def __start_tracer(self):
        """Start bpftrace and rotate logs while reading stdout."""
        bt_cmd = ["bpftrace"] + self.__options + [self.__script] + self.__args
        logging.debug(f"[{self.__tid}] starting tracer: {' '.join(bt_cmd)}")

        # Setup first output file
        self.__open_new_file()

        try:
            proc = subprocess.Popen(
                bt_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # line-buffered read
            )

            # Read until process ends or stop requested
            while True:
                if self.__stop_event.is_set():
                    logging.debug(f"[{self.__tid}] stopping tracer")
                    proc.terminate()
                    try:
                        proc.wait(timeout=self.__tto)
                    except subprocess.TimeoutExpired:
                        logging.debug(f"[{self.__tid}] killing tracer")
                        proc.kill()
                    break

                # Non-blocking line read
                line = proc.stdout.readline()
                if not line:
                    # process probably exited
                    if proc.poll() is not None:
                        break
                    time.sleep(0.05)
                    continue

                # Write line safely with rotation
                self.__write_line(line)

        except Exception as e:
            logging.error(f"[{self.__tid}] tracer failed: {e}")

        finally:
            if self.__f:
                self.__f.close()
            logging.debug(f"[{self.__tid}] exiting tracer")
