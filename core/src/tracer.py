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
        self.tid = tid  # tracer id
        self.options = []  # bpftrace options
        self.args = []  # bpftrace input arguments
        self.script = script  # bpftrace script
        self.tto = termination_timeout

    def with_options(self, options: list[str]):
        """
        Add options to the tracer.

        :param options: a list of options to append the current options
        """
        self.options.append(options)

    def with_args(self, args: list[str]):
        """
        Add args to the tracer.

        :param args: a list of args to append the current args
        """
        self.args.append(args)

    def __start_tracer(self):
        """Start tracer in a new process and wait until its over or the stop event is received."""
        # create the bpftrace command
        bt_command = ["bpftrace"] + self.options + [self.script] + self.args

        logging.debug("[{}] starting tracer: {}".format(self.tid, " ".join(bt_command)))

        # run a new process
        proc = subprocess.Popen(bt_command)
        try:
            while proc.poll() is None:
                if self.stop_event.is_set():
                    logging.debug(f"[{self.tid}] stopping tracer")
                    proc.terminate()
                    try:
                        logging.debug(f"[{self.tid}] waiting for {self.tto}s")
                        proc.wait(timeout=self.tto)
                    except subprocess.TimeoutExpired:
                        logging.debug(f"[{self.tid}] killing tracer")
                        proc.kill()
                    return
                time.sleep(0.2)
        finally:
            logging.debug(f"[{self.tid}]  exiting tracer")

    def start(self):
        """Start a tracer by calling the __start_tracer in a thread."""
        self.stop_event = threading.Event()
        self.t = threading.Thread(target=self.__start_tracer, args=(), daemon=True)
        self.t.start()

    def stop(self):
        """Stop the tracer by terminating its process and thread."""
        self.stop_event.set()
        self.t.join()

    def wait(self):
        """Wait for the tracing process to finish."""
        self.t.join()
