import re

class BaseModule(object):
    def __init__(self, mud):
        self.mud = mud
        # self.world = mud.world
        # self.state = mud.world.state
        self.aliases = {}
        self.triggers = {}

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
