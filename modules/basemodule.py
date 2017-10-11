import re
import threading
import time


class BaseModule(object):
    timer_thread = None
    stopflag = None
    timers = {}
    previous_checkpoint = time.time()

    def __init__(self, mud):
        self.mud = mud
        self.aliases = self.getTriggers()
        self.triggers = self.getTriggers()

        # Timers are names mapped to tuples of (oneshot, period, remaining time until period boundary, callable)
        BaseModule.timers.update(self.getTimers())

        if not BaseModule.stopflag:
            BaseModule.stopflag = threading.Event()
        if not BaseModule.timer_thread:
            BaseModule.timer_thread = threading.Thread(target=BaseModule.timer_thread_fn)
            BaseModule.timer_thread.start()

    @staticmethod
    def timer_thread_fn():
        while not BaseModule.stopflag.is_set():
            now = time.time()
            delta = now - BaseModule.previous_checkpoint
            BaseModule.timeslice(delta)
            BaseModule.previous_checkpoint = now
            time.sleep(0.1)

    @staticmethod
    def timeslice(delta):
        def update(name, rem_time):
            timer = BaseModule.timers[name]
            BaseModule.timers[name] = (timer[0], timer[1], rem_time, timer[3])
            return rem_time

        remove = []
        for name, timer in BaseModule.timers.items():
            oneshot, period, remaining, fn = timer
            remaining = update(name, remaining - delta)
            if remaining < 0:
                if oneshot:
                    remove.append(name)
                else:
                    update(name, period)
                fn()

        for name in remove:
            del BaseModule.timers[name]

    @staticmethod
    def mktimer(delay, fn, oneshot=False):
        return (oneshot, delay, delay, fn)

    def send(self, line):
        return self.mud.send(line)

    def log(self, *args, **kwargs):
        return self.mud.log(*args, **kwargs)

    def alias(self, line):
        if line in self.aliases:
            self.mud.send(self.aliases[line])
            return True

    def trigger(self, raw, stripped):
        for trigger, response in self.triggers.items():
            if re.match(trigger, stripped):
                if isinstance(response, str):
                    self.send(response)
                else:
                    output = response(self, re.match(trigger, stripped).groups())
                    if output:  # might be for side effects
                        self.send(output)
                break

    def getTriggers(self):
        return {}

    def getAliases(self):
        return {}

    def getTimers(self):
        return {}

    def quit(self):
        if BaseModule.stopflag:
            BaseModule.stopflag.set()
        if BaseModule.timer_thread:
            BaseModule.timer_thread.join()
        BaseModule.timer_thread = None
        BaseModule.stopflag = None
