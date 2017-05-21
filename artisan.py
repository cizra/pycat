import importlib
import base
import coffee
importlib.reload(coffee)
import collections
import random
import re
import subprocess


def startForaging(mud, _):
    mud.state['forage'] = 'started'
    return 'forage'


def forageResults(mud, matches):
    mud.state['forage'] = 'found'
    return 'put {} drum\nfoodprep drum'.format(matches[0]),


def forageDone(mud, _):
    if mud.state['forage'] != 'found':
        return 'light fire'

def nothingToMine(mud, _):
    dirs = list(mud.gmcp['room']['info']['exits'].keys())
    return random.choice(dirs) + '\n' + 'warrants\nmastermine'

def nothingToDig(mud, _):
    dirs = list(mud.gmcp['room']['info']['exits'].keys())
    return random.choice(dirs) + '\n' + 'gemdig'

def debundle(mud, _):
    exits = list(mud.gmcp['room']['info']['exits'].keys())
    if len(exits) == 6:
        exit = 'u'
    else:
        exit = exits[0]
    rexit = base.reverse(exit)
    return 'drag bundle {}\n{}'.format(exit, rexit)

ALIASES = {
        }
TRIGGERS = {
        'You are hungry.': 'eat bread',
        'You are thirsty.': 'drink barrel',
        "You don't see 'bread' here.": 'quit;y',

        # pierce -> remove pierce -> cup -> tattoo -> remove tattoo -> carve

        'You are done building a fire.': startForaging,
        # 'You manage to gather .* pounds? of (.*)\.': forageResults,
        'You are done foraging.': 'light fire', # forageDone,
        'You are done making .* preserves.': 'get all drum\ndrop all preserves',
        'You are done making .* preserves.': 'get all drum\nforage',
        
        "You can't seem to find anything worth mining here.": nothingToMine,
        "You can't seem to find anything worth digging up here.": nothingToDig,
        'You manage to mine .* pounds of (.*)\.': lambda mud, matches: 'mastermine bundle all {}\nmastermine'.format(matches[0]),
        'You manage to dig out .* .*\.': 'gemdig',

        # '.*Some (.*) sits here\.': lambda mud, matches: 'mastermine bundle all ' + matches[0],

        # 'A \d+# .* bundle is here.': debundle,
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
        # if self.speculate(line):
        #     return

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
