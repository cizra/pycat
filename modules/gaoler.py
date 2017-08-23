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
    mud.world.modules['mapper'].go(-565511213)
    mud.send('fill barrel sink\ndrink sink\ndrink sink\nn\nn\nmastermine')

def goMine(mud, _):
    mud.world.modules['mapper'].go(-565509103)
    mud.send('mastermine')

def buyBread(mud, _):
    mud.send('remove axe')
    mud.send('remove axe')
    mud.world.modules['mapper'].go('baker')
    mud.send('buy 120 bread')
    mud.send('run s e 4s w 2s e 2n')
    mud.send('open w')
    mud.send('run w s')
    mud.send('wield axe')
    mud.send('hold axe')
    mud.send('chop')


class Gaoler(BaseModule):
    def getTriggers(self):
        return {
            'You are thirsty.': 'drink barrel',
            'You are hungry.': 'eat bread',
            # 'You are done building a fire.': 'chop',
            'You manage to chop up \d+ pounds? of (\w+)\.': lambda  world, matches: 'chop bundle all ' + matches[0] + '\ncarve chopstick',
            'You manage to mine \d+ pounds? of (.+)\.': lambda world, matches: \
                    'mastermine bundle all {}\nmastermine'.format(matches[0]),
            'You are done chopping.': 'chop',
            'You can\'t seem to find anything worth mining here.': nothingToMine,
            'You can\'t seem to find any trees worth cutting around here.': nothingToChop,
            'You can\'t find anything to chop here.': 'fill barrel sink\nrun 2s\nchop',
            # 'You don\'t see .* here.': 'light fire',
            # 'You can\'t see to do that!': 'light fire',
            'A wood barrel is empty.': getWater,
            'You need to stand up!': 'stand\nmastermine',
            'If you don\'t do something, you will be logged out in 5 minutes!': 'stand\nmastermine',
            'A wood barrel is empty.': getWater,
            'You don\'t think this is a good place to mine.': goMine,
            'You are done carving .*.': 'chop',
            }


def getClass():
    return Gaoler
