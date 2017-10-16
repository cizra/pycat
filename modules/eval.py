from modules.basemodule import BaseModule
from pprint import pformat


class Eval(BaseModule):
    def alias(self, line):
        if line.startswith('#py '):
            rest = line[4:]
            self.mud.log("\n" + pformat(eval(rest)))
            return True
        elif line.startswith('#pye '):
            rest = line[5:]
            exec(rest)
            return True
