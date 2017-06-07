from modules.basemodule import BaseModule

import random
import re


def nothingToMine(mud, _):
    dirs = list(mud.gmcp['room']['info']['exits'].keys())
    return random.choice(dirs) + '\n' + 'mastermine'


ALIASES = {
        }
TRIGGERS = {
        'You are thirsty.': 'drink barrel',
        'You are hungry.': 'eat bread',
        'You are done building a fire.': 'chop',
        'You manage to chop up \d+ pounds? of (\w+)\.': lambda  world, matches: 'chop bundle all ' + matches[0],
        'You manage to mine \d+ pounds? of (\w+)\.': lambda world, matches: \
                'mastermine bundle all {}\nmastermine'.format(matches[0]),
        'You are done chopping.': 'light fire',
        'You can\'t seem to find anything worth mining here.': nothingToMine,
        }


class Gaoler(BaseModule):
    def __init__(self, mud):
        super().__init__(mud)
        self.aliases.update(ALIASES)
        self.triggers.update(TRIGGERS)


def getClass():
    return Gaoler
