class BaseModule(object):

    def __init__(self, mud):
        self.mud = mud

    def send(self, line):
        return self.mud.send(line)

    def show(self, line):
        return self.mud.show(line)

    def log(self, *args, **kwargs):
        return self.mud.log(*args, **kwargs)

    def getTriggers(self):
        return {}

    def getAliases(self):
        return {}

    # Timers are names mapped to tuples of (oneshot, period, remaining time until period boundary, callable)
    def getTimers(self):
        return {}

    def mktimer(self, *args):
        return self.world.mktimer(*args)

    def mkdelay(self, *args):
        return self.world.mkdelay(*args)

    def quit(self):
        pass
