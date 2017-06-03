from modules.basemodule import BaseModule


class Eval(BaseModule):
    def alias(self, line):
        if line.startswith('#py '):
            rest = line[4:]
            self.mud.log(repr(eval(rest)))
            return True
        elif line.startswith('#pye '):
            rest = line[5:]
            exec(rest)
            return True
