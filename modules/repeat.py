from modules.basemodule import BaseModule
import collections


class Repeat(BaseModule):
    def __init__(self, mud):
        super().__init__(mud)
        self.outlog = collections.deque(maxlen=20)

    def alias(self, line):
        if line == '':
            if len(self.outlog) > 0:
                self.mud.send(self.outlog[0])
            # Signal to the client that the alias has consumed the input line
            return True
        elif line == '#nl':
            self.mud.send('')
            return True  # Consume input line
        else:
            self.outlog.appendleft(line)

