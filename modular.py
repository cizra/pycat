import re


def stack(line):
    assert('\n' not in line)
    out = []
    startmatch = 0
    for i in range(1, len(line) - 1):
        if line[i] == ';' and line[i-1] != ';' and line[i+1] != ';':
            out.append(line[startmatch:i].replace(';;', ';'))
            startmatch = i + 1
    out.append(line[startmatch:].replace(';;', ';'))
    return out


class ModularClient(object):
    def __init__(self, mud):
        # self.modules must be set up by child class
        self.mud = mud
        self.state = {}
        self.gmcp = {}
        for m in self.modules.values():
            m.world = self
            m.gmcp = self.gmcp

    def getHostPort(self):
        for m in self.modules.values():
            if hasattr(m, 'getHostPort'):
                return m.getHostPort()
        return input("Hostname: "), input("Port: ")

    def alias(self, line):
        # It's possible to move command stacking and spamrepeat into modules, at the cost of horribly complicating
        # everything in this function. Implementing them here results in less overall ugliness.
        sublines = stack(line)
        if len(sublines) > 1:
            for subline in sublines:
                if not self.alias(subline):
                    self.mud.send(subline)
            return True
        else:
            line = sublines[0]

        if re.match(r'#\d+ .+', line):
            match = re.match(r'#(\d)+ (.+)', line)
            times, cmd = match.groups()
            for i in range(int(times)):
                if not self.alias(cmd):
                    self.mud.send(cmd)
            return True

        for module in self.modules.values():
            # If alias wants to signal that it consumed the command, return True -- it won't be sent to MUD then
            # Otherwise, the line is sent to MUD
            if hasattr(module, 'alias'):
                if module.alias(line):
                    return True
        return False

    def trigger(self, raw):
        stripped = self.mud.strip_ansi(raw).strip()
        replacement = None
        for module in self.modules.values():
            if hasattr(module, 'trigger'):
                repl = module.trigger(raw, stripped)
                if replacement is None and repl is not None:  # modules come in order of priority, so first one wins
                    replacement = repl
        return replacement

    def handleGmcp(self, cmd, value):
        for module in self.modules.values():
            if hasattr(module, 'handleGmcp'):
                module.handleGmcp(cmd, value)

    def quit(self):
        for module in self.modules.values():
            if hasattr(module, 'quit'):
                module.quit()


def getClass():
    return ModularClient
