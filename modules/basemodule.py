class BaseModule(object):

    def __init__(self, mud):
        self.mud = mud

    def send(self, line):
        return self.mud.send(line)

    def log(self, *args, **kwargs):
        return self.mud.log(*args, **kwargs)

    def getTriggers(self):
        return {}

    def getAliases(self):
        return {}

    # Timers are names mapped to tuples of (oneshot, period, remaining time until period boundary, callable)
    def getTimers(self):
        return {}

    def mktimer(self, period, fn):
        return self.world.mktimer(period, fn)

    def quit(self):
        pass
