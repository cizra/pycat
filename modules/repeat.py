from modules.basemodule import BaseModule
import collections


class Repeat(BaseModule):
    def __init__(self, mud):
        super().__init__(mud)
        self.outlog = collections.deque(maxlen=20)

    def alias(self, line):
        if line == '':
            self.mud.send(self.outlog[0])
        elif line == '#nl':
            self.mud.send('')
        else:
            self.outlog.appendleft(line)
