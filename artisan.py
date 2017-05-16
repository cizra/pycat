import importlib
import coffee
importlib.reload(coffee)
import collections
import re
import subprocess


ALIASES = {
        }
TRIGGERS = {
        }
NOTIFICATIONS = {
        }


class Artisan(coffee.Coffee):
    def __init__(self, mud):
        super().__init__(mud)
        self.aliases.update(ALIASES)
        self.triggers.update(TRIGGERS)
        self.notifications.update(NOTIFICATIONS)

    def trigger2(self, line):
        super().trigger2(line)
        if self.speculate(line):
            return

    def speculate(self, line):
        # desirables = {'masterchop': ['wood', 'redwood', 'willow', 'oak'], 'mastermine': {'mithril', iro
        desirables_re = '(coal|wood|mithril|oak|redwood|willow|hickory)'
        if 'speculate' not in self.state:
            self.state['speculate'] = None
        if (
                re.match('^You think this spot would be good for mithril\.', line) or
                re.match('^You think this spot would be good for (oak|wood|willow|redwood|hickory)\.', line) or
                re.match(r'^You manage to mine \d+ pounds of {}\.$'.format(desirables_re), line)
                ):
            return self.send('mastermine')
        elif re.match('^You manage to chop up \d+ pounds of {}\.$'.format(desirables_re), line):
            return self.send('masterchop')
        elif self.state['speculate'] != 'mining' and re.match(r'There looks like {} to the (.+)\.'.format(desirables_re), line):
            self.state['speculate'] = 'mining'
            direction = re.match(r'There looks like {} to the (.+)\.'.format(desirables_re), line).group(2)
            return self.send(direction + '\nmastermine')
        elif line == 'Your speculate attempt failed.':
            return self.send('speculate')
        elif (line ==  'You can\'t seem to find anything worth mining here.' or
                line == 'You can\'t seem to find any trees worth cutting around here.'):
            self.state['speculate'] = 'checking exits'
            return self.send('exits brief')
        elif self.state['speculate'] == 'checking exits':
            match = re.match('^\[Exits: (\w+)\]$', line) 
            if not match:
                match = re.match('^\[Exits: \w+ (\w+)\]$', line)
            direction = match.group(1)
            return self.send(direction + '\nspeculate')
        elif self.state['speculate'] == 'checking exits' and re.match('^\[Exits: \w+ \w+ .*\]$', line):
            self.state['speculate'] = 'speculating'
            return self.send('speculate')


def get_class():
    return Artisan
