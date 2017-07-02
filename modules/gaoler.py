from modules.basemodule import BaseModule

import random
import re


def nothingToMine(mud, _):
    dirs = list(mud.gmcp['room']['info']['exits'].keys())
    return random.choice(dirs) + '\n' + 'mastermine'

def nothingToChop(mud, _):
    dirs = list(mud.gmcp['room']['info']['exits'].keys())
    return random.choice(dirs) + '\n' + 'chop'

def getWater(mud, _):
    mud.send(mud.world.mapper.path(-565510123) + '\nfill barrel sink\ndrink sink\ndrink sink\nmastermine')


ALIASES = {
        }
TRIGGERS = {
        'You are thirsty.': 'drink barrel',
        'You are hungry.': 'eat bread',
        'You are done building a fire.': 'chop',
        'You manage to chop up \d+ pounds? of (\w+)\.': lambda  world, matches: 'chop bundle all ' + matches[0] + '\nchop',
        'You manage to mine \d+ pounds? of (.+)\.': lambda world, matches: \
                'mastermine bundle all {}\nmastermine'.format(matches[0]),
        'You are done chopping.': 'chop',
        'You can\'t seem to find anything worth mining here.': nothingToMine,
        'You can\'t seem to find any trees worth cutting around here.': nothingToChop,
        'You can\'t find anything to chop here.': 'run 3s\nchop',
        'You don\'t see .* here.': 'light fire',
        'You can\'t see to do that!': 'light fire',
        'A wood barrel is empty.': getWater,
        'You need to stand up!': 'stand\nchop',
        }


class Gaoler(BaseModule):
    def __init__(self, mud):
        super().__init__(mud)
        self.aliases.update(ALIASES)
        self.triggers.update(TRIGGERS)


def getClass():
    return Gaoler
