from modules.basemodule import BaseModule

import random
import re


def nothingToForage(mud, _):
    dir = random.choice(list(mud.gmcp['room']['info']['exits'].keys()))
    if mud.gmcp['room']['info']['exits'][dir] == -565511086:
        return 'run 5e\nforage'
    else:
        return dir + '\n' + 'forage'

def nothingToMine(mud, _):
    dirs = list(mud.gmcp['room']['info']['exits'].keys())
    return random.choice(dirs) + '\n' + 'mastermine'

def nothingToChop(mud, _):
    dirs = list(mud.gmcp['room']['info']['exits'].keys())
    return random.choice(dirs) + '\n' + 'chop'

def getWater(mud, _):
    mud.world.modules['mapper'].go(-420699692)
    mud.send('fill barrel sink\ndrink sink\ndrink sink\ns\ne\nforage')

def goMine(mud, _):
    mud.world.modules['mapper'].go(-565509103)
    mud.send('mastermine')

def buyBread(mud, _):
    mud.send('recall')
    mud.send('run 2s w n')
    mud.send('buy 120 bread')
    mud.send('eat bread')
    mud.send('run s e 4s w 2s e 2n')
    mud.send('unlock w')
    mud.send('open w')
    mud.send('w')
    mud.send('lock e')
    mud.send('run s e')
    mud.send('forage')


class Gaoler(BaseModule):
    def getTriggers(self):
        return {
            'You are thirsty.': 'drink barrel',
            'You are hungry.': 'eat bread',
            # 'You are done building a fire.': 'chop',
            'You manage to chop up \d+ pounds? of (\w+)\.': lambda  world, matches: 'chop bundle all ' + matches[0] + '\nspeculate',
            'You manage to mine \d+ pounds? of (.+)\.': lambda world, matches: \
                    'mastermine bundle all {}\nmastermine'.format(matches[0]),
            'You manage to gather \d+ pounds? of (\w+)\.': lambda  world, matches: 'forage bundle all ' + matches[0] + '\nforage',
            'You are done chopping.': 'chop',
            # 'You are done foraging.': 'forage',
            'You can\'t seem to find anything worth mining here.': nothingToMine,
            'You can\'t seem to find any trees worth cutting around here.': nothingToChop,
            'You can\'t seem to find anything worth foraging around here.': nothingToForage,
            # 'You can\'t find anything to chop here.': 'fill barrel sink\nrun 2s\nchop',
            'You don\'t see \'bread\' here.': buyBread,
            'You don\'t seem to have \'bread\'.': buyBread,
            # 'You can\'t see to do that!': 'light fire',
            'A wood barrel is empty.': getWater,
            'You need to stand up!': 'stand\nmastermine',
            'If you don\'t do something, you will be logged out in 5 minutes!': 'stand\nmastermine',
            'You don\'t think this is a good place to mine.': goMine,
            'You are done carving .*.': 'chop',
            'You are done speculating.': 'mastermine',
            'You can\'t carry that many items.': 'drop all.pound\ndrop all.bundle',
            }

    def getTimers(self):
        return {
                "hone": self.mktimer(60*5 + 5, lambda: self.send("bodypie grumpy ears\nirrig title On a pond\nexcav title On a pond\nlandscap title On a pond\nweave hair ribbon\nrun 2e\nmarm Spiked Banded Handguards\ninstrum a pair of clappers\nrun w d\nmastermine\nrun u w\nappraise ice\nmasterfish\nspeculate"))
                }

def getClass():
    return Gaoler
