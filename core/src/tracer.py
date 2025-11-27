import logging
import subprocess
import threading
import time


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

        logging.debug("[{}] starting tracer: {}".format(self.__tid, " ".join(bt_command)))

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
