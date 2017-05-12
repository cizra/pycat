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
        'You are hungry.': 'hgr',
        'You are thirsty.': 'thr',
        }

class BaseClient(object):
    def __init__(self, mud):
        self.mud = mud
        self.state = {}
        self.state['outlog'] = collections.deque(maxlen=20)
        self.aliases = ALIASES
        self.triggers = TRIGGERS
        self.notifications = NOTIFICATIONS
    
    def get_host_port():
        return input("Hostname: "), input("Port: ")

    def log(self, *args):
        self.mud.log(*args)

    def send(self, line):
        self.state['outlog'].append(line)
        self.mud.send(line)

    def alias(self, line):
        def send(line):
            if 'record' in self.state:
                self.state['record'].append(line)
            self.state['outlog'].append(line)
            self.mud.send(line)
            return True

        if line.startswith('#py '):
            rest = line[3:]
            self.log(repr(eval(rest)))
            return True
        elif line == '#record':
            self.log("Started recording. Send #recordoff to end.")
            STATE['record'] = []
            return True
        elif line == '#recordoff' and 'record' in self.state:
            self.log("Recorded steps:")
            self.log(STATE['record'])
            del self.state['record']
            return True
        elif re.match(r'#\d+ .+', line):
            match = re.match(r'#(\d)+ (.+)', line)
            times, cmd = match.groups()
            return send('\n'.join([cmd] * int(times)))
        elif line in self.aliases:
            self.send(self.aliases[line])
            return True

        return send(line)

    def trigger(self, line):
        line = self.mud.strip_ansi(line).strip()
        if line in self.notifications:
            notify(self.notifications[line])
        # fallthrough, allow both notification and trigger
        if line in self.triggers:
            self.send(self.triggers[line])
        # fallthrough, allow subclass to add reaction
        return self.trigger2(line)

    def trigger2(self, line):
        pass

    def gmcp(self, cmd):
        # self.log('Got GMCP', cmd)
        pass


def get_class():
    return BaseClient
