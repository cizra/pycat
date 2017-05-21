import collections
import re
import subprocess


def notify(msg):
    subprocess.call(['notify-send', 'CfM', msg])


ALIASES = {
        }
TRIGGERS = {
        }
NOTIFICATIONS = {
        'You are hungry\.': 'hgr',
        'You are thirsty\.': 'thr',
        '.* is DEAD!!!': 'dd',
        }


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


class BaseClient(object):
    def __init__(self, mud):
        self.mud = mud
        self.state = {}
        self.gmcp = {}
        self.state['outlog'] = collections.deque(maxlen=20)
        self.aliases = ALIASES
        self.triggers = TRIGGERS
        self.notifications = NOTIFICATIONS
        self.logfile = open('session.log', 'a', buffering=1)
    
    def get_host_port():
        return input("Hostname: "), input("Port: ")

    def log(self, *args):
        self.mud.log(*args)

    def send(self, line):
        self.state['outlog'].append(line)
        self.mud.send(line)

    def alias(self, line):
        sublines = stack(line)
        if len(sublines) > 1:
            for subline in sublines:
                self.alias(subline)
            return True

        def send(line):
            if 'record' in self.state:
                self.state['record'].append(line)
            self.state['outlog'].append(line)
            self.mud.send(line)
            return True
        if not line:
            return send('!')
        elif line.startswith('#py '):
            rest = line[4:]
            self.log(repr(eval(rest)))
            return True
        elif line.startswith('#pye '):
            rest = line[5:]
            exec(rest)
            return True
        elif line == '#record on':
            self.log("Started recording. Send #record off to end, or #record undo to undo.")
            self.state['record'] = []
            return True
        elif line == '#record off' and 'record' in self.state:
            self.log("Recorded steps:")
            self.log(self.state['record'])
            del self.state['record']
            return True
        elif line == '#record undo' and 'record' in self.state:
            self.state['record'].pop()
            return True
        elif re.match(r'#\d+ .+', line):
            match = re.match(r'#(\d)+ (.+)', line)
            times, cmd = match.groups()
            return send('\n'.join([cmd] * int(times)))
        elif line.startswith('#grep '):
            arg = line[len('#grep '):]
            grep = subprocess.Popen(['grep', arg, 'session.log'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = grep.communicate(timeout=5)
            self.log('\n' + out.decode('utf-8'))
            return True
        elif line in self.aliases:
            for subline in stack(self.aliases[line]):
                self.send(subline)
            return True

        return send(line)

    def trigger(self, line):
        self.logfile.write(line + '\n')
        line = self.mud.strip_ansi(line).strip()
        for match, result in self.notifications.items():
            if re.match(match, line):
                notify(result)
        # fallthrough, allow both notification and trigger
        for trigger, response in self.triggers.items():
            if re.match(trigger, line):
                if isinstance(response, str):
                    self.send(response)
                else:
                    output = response(self, re.match(trigger, line).groups())
                    if output:  # might be for side effects
                        self.send(output)
        # fallthrough, allow subclass to add reaction
        return self.trigger2(line)

    def trigger2(self, line):
        pass

    def handleGmcp(self, cmd, value):
        # self.log('Got GMCP', cmd, value)
        pass


def get_class():
    return BaseClient
