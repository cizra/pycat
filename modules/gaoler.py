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
    mud.send(mud.world.modules['mapper'].path(-420699692) + '\nfill barrel sink\ndrink sink\ndrink sink\ns\nchop')

def buyBread(mud, _):
    mud.send('remove axe')
    mud.send('remove axe')
    mud.world.modules['mapper'].go('baker')
    mud.send('buy 120 bread')
    mud.send('run s e 4s w 2s e 2n')
    mud.send('wield axe')
    mud.send('hold axe')
    mud.send('chop')


class Gaoler(BaseModule):
    def getTriggers(self):
        return {
            'You are thirsty.': 'drink barrel',
            'You are hungry.': 'eat bread',
            'You are done building a fire.': 'chop',
            'You manage to chop up \d+ pounds? of (\w+)\.': lambda  world, matches: 'chop bundle all ' + matches[0] + '\nchop',
            'You manage to mine \d+ pounds? of (.+)\.': lambda world, matches: \
                    'mastermine bundle all {}\nmastermine'.format(matches[0]),
            'You are done chopping.': 'chop',
            'You can\'t seem to find anything worth mining here.': nothingToMine,
            'You can\'t seem to find any trees worth cutting around here.': nothingToChop,
            'You can\'t find anything to chop here.': 'fill barrel sink\nrun 2s\nchop',
            'You don\'t see .* here.': 'light fire',
            'You can\'t see to do that!': 'light fire',
            'A wood barrel is empty.': getWater,
            'You need to stand up!': 'stand\nchop',
            'If you don\'t do something, you will be logged out in 5 minutes!': 'stand\nchop',
            'A wood barrel is empty.': getWater,
            'You don\'t seem to have \'bread\'.': buyBread,
            }


def getClass():
    return Gaoler
