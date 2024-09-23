from modules.basemodule import BaseModule
from pprint import pformat


class Eval(BaseModule):
    def alias(self, line):
        if line.startswith(self.mud.cmd_char + 'py '):
            rest = line[4:]
            self.mud.log("\n" + pformat(eval(rest)))
            return True
        elif line.startswith(self.mud.cmd_char + 'pye '):
            rest = line[5:]
            exec(rest)
            return True
