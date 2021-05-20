from threading import Thread, Event
from typing import Callable, List, Dict


class TimedJobThread(Thread):
    def __init__(self, interval: float, execute: Callable, args: List=[], kwargs: Dict={}):
        Thread.__init__(self)
        self.daemon = False
        self.stopped = Event()
        self.interval = interval
        self.execute = execute
        self.args = args
        self.kwargs = kwargs


    def start(self):
        if self.stopped.is_set():
            self.stopped.clear()
        super().start()


    def stop(self):
        if not self.stopped.is_set():
            self.stopped.set()


    def run(self):
        while not self.stopped.wait(self.interval):
            self.execute(*self.args, **self.kwargs)
