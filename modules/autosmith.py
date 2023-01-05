from modules.basemodule import BaseModule

import pprint
import random
import re
import time
import urllib.request


def nothingToForage(mud, _):
    dir = random.choice(list(mud.gmcp['room']['info']['exits'].keys()))
    if mud.gmcp['room']['info']['exits'][dir] == -565511086:
        return 'run 5e\nforage'
    else:
        return dir + '\n' + 'forage'

def nothingToMine(mud, _):
    dirs = list(mud.gmcp['room']['info']['exits'].keys())
    if len(dirs) == 1:
        return dirs[0] + '\n' + 'speculate'
    else:
        return "speculate"

def nothingToChop(mud, _):
    dirs = list(mud.gmcp['room']['info']['exits'].keys())
    return random.choice(dirs) + '\n' + 'chop'

def goMine(mud, _):
    mud.modules['mapper'].go(-565509103)
    mud.send('mastermine')

def buyBread(mud, _):
    return
    mud.send('recall')
    mud.send('run 2s w n')
    mud.send('buy 120 bread')
    mud.send('run s e 4s w 2s e 2n')
    mud.send('unlock w')
    mud.send('open w')
    mud.send('w')
    mud.send('lock e')
    mud.send('speculate')


def smith(mud, _):
    if mud.name != 'landscapegoat':
        return

    if 'task_start_time' in mud.state:
        mud.log("The task took {}s".format(time.time() - mud.state['task_start_time']))

    level = mud.level()

    if 'smithing' not in mud.state or mud.state['smithing'] == 6:
        mud.state['smithing'] = 0

    if mud.state['smithing'] == 0:
        mud.send('get all.supple\nput all.supple trash')
        smithable = mud.state['smithables_carve'][level]
    else:
        smithable = mud.state['smithables_carve'][0]

    mud.state['smithing'] += 1

    return "carve supple {arg}".format(arg=smithable)

def failSmithing(mud, _):
    if 'smithing' in mud.state:
        mud.state['smithing'] -= 1


def speculateFor(mud, groups):
    mud.state['speculate'] = {
            'direction': groups[0],
            'targets': groups[1].split(' '),
            'success': True,
            }
    mud.send("speculate")

def specLine(mud, groups):
    if 'speculate' not in mud.state:
        return
    fixdir = {
            'below': 'd',
            'above you': 'u',
            'to the north': 'n',
            'to the east': 'e',
            'to the south': 's',
            'to the west': 'w',
            '.': '',  # here
            }
    resource, direction = groups
    direction = fixdir[direction]
    if 'results' not in mud.state['speculate']:
        mud.state['speculate']['results'] = {}
    mud.state['speculate']['results'][resource] = direction

def speculateFailed(mud, _):
    if 'speculate' in mud.state:
        mud.state['speculate']['success'] = False

def speculateDoublecheck(mud, matches):
    if 'speculate' in mud.state:
        if matches[0] not in mud.state['speculate']['targets']:
            return nothingToMine(mud, matches)

def speculateDone(mud, _):
    if 'speculate' in mud.state:
        if not mud.state['speculate']['success']:
            mud.state['speculate']['success'] = True
            return "speculate"

        resource_to_skill = {
                'mithril': 'mastermine',
                'iron': 'mastermine',
                'coal': 'mastermine',
                'silk': 'masterforage',
                'sugar': 'masterforage',
                }
        for tgt in mud.state['speculate']['targets']:
            if 'results' in mud.state['speculate'] and tgt in mud.state['speculate']['results']:
                mud.send("{}\n{}".format(mud.state['speculate']['results'][tgt], resource_to_skill[tgt]))
                break
        else:
            ex = list(map(lambda s: s.lower(), mud.gmcp['room']['info']['exits'].keys()))
            reverse = {
                    'n': 's',
                    'e': 'w',
                    's': 'n',
                    'w': 'e',
                    'u': 'd',
                    'd': 'u',
                    }
            if mud.state['speculate']['direction'] in ex:
                go = mud.state['speculate']['direction']
            elif reverse[mud.state['speculate']['direction']] in ex:
                go = mud.state['speculate']['direction'] = reverse[mud.state['speculate']['direction']]
            else:
                go = random.choice(ex)
            mud.send(go + "\nspeculate")
    mud.state['speculate']['results'] = {}

def mined(mud, matches):
    resource = matches[0]
    here = mud.modules['mapper'].current()
    path = mud.modules['mapper'].path('565511209')
    rpath = mud.modules['mapper'].path2('565511209', here)
    return 'mastermine bundle all {resource}\nget {resource} bundle\n{path}\ndrink sink\ndrop {resource} bundle\nlook {resource} bundle\n{rpath}\nmastermine'.format(resource=resource, path=path, rpath=rpath)


def startScrapping(mud, groups):
    mud.state['scrapping'] = groups[0]
    mud.send('scrap ' + groups[0])

def stopScrapping(mud, groups):
    del mud.state['scrapping']
    mud.log("Removed scrap triggers")

def scrapAgain(mud, groups):
    if 'scrapping' in mud.state:
        mud.send("scrap " + mud.state['scrapping'])


def scrapeItems(mud, groups):
    # TODO: choose skill
    skill = 'carve'
    with urllib.request.urlopen('https://raw.githubusercontent.com/bozimmerman/CoffeeMud/master/resources/skills/carpentry.txt') as f:
        skill_file = f.read().decode('utf-8')

    class Item(object):
        name = None
        level = None
        craftingTime = None
        cost = None
        value = None
        itemClass = None

        def __repr__(self):
            return "{} level={} time={} cost={}".format(self.name, self.level, self.craftingTime, self.cost)

    items = []
    for line in skill_file.split('\r\n'):
        # Format of the files is defined in corresponding skill source, eg. com/planet_ink/coffee_mud/Abilities/Common/Armorsmithing.java: 
        # "ITEM_NAME\tITEM_LEVEL\tBUILD_TIME_TICKS\tMATERIALS_REQUIRED\t"
        # "ITEM_BASE_VALUE\tITEM_CLASS_ID\tCODED_WEAR_LOCATION\tCONTAINER_CAPACITY\t"
        # "BASE_ARMOR_AMOUNT\tCONTAINER_TYPE\tCODED_SPELL_LIST";
        if not line:
            continue
        columns = line.split('\t')
        item = Item()
        item.name = columns[0].replace('% ', '')
        item.level = int(columns[1])
        item.craftingTime = int(columns[2])
        item.cost = int(columns[3])
        item.value = int(columns[4])
        item.itemClass = columns[5]
        items.append(item)

    # prioritize fast exp gain over low material cost by sorting by time
    lowLevelItems = list(filter(lambda item: item.level <= 6, items))
    filler = sorted(
                sorted(lowLevelItems
                , key=lambda item: item.cost)
            , key=lambda item: item.craftingTime)[0]

    itemsPerLevel = {}
    for item in items:
        if item.level not in itemsPerLevel:
            itemsPerLevel[item.level] = []
        itemsPerLevel[item.level].append(item)

    craftPerLevel = {}
    for level, itemsPerLevel in itemsPerLevel.items():
        sortedByBenefit = sorted(itemsPerLevel, key=lambda item: (5 * filler.craftingTime + item.craftingTime) / (5 * filler.cost + item.cost))
        craftPerLevel[level] = sortedByBenefit[-1].name

    substs = []
    for i in range(1, 91):
        if i not in craftPerLevel:
            substs.append(i)
            craftPerLevel[i] = craftPerLevel[i - 1]
    if substs:
        mud.log("Added substitutions for these: {}".format(substs))

    craftPerLevel[0] = filler.name

    mud.state['smithables_' + skill] = craftPerLevel
    mud.log("Done")


class AutoSmith(BaseModule):
    def getAliases(self):
        return {
                'scrape (.+)': scrapeItems,
                'smith': smith,
                'autoscrap (.*)': startScrapping,
                'stopscrap': stopScrapping,
                'specfor (.) (.*)': speculateFor,
                }

    def getTriggers(self):
        return {
            'You are done scrapping.': scrapAgain,
            # 'You don\'t have enough here to get anything from.': 'get agile\nscrap agile',
            'You are thirsty.': 'drink sink',
            'You are hungry.': 'eat bread',
            # 'You are done building a fire.': 'chop',
            'You manage to chop up \d+ pounds? of (\w+)\.': lambda  world, matches: 'chop bundle all ' + matches[0] + '\nspeculate',
            'You manage to mine \d+ pounds? of (.+)\.': mined,
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
            'You need to stand up!': 'stand\nmastermine',
            'If you don\'t do something, you will be logged out in 5 minutes!': 'stand\nmastermine',
            'You don\'t think this is a good place to mine.': goMine,
            'There looks like (.*) (below|above you|to the north|to the east|to the south|to the west).': specLine,
            'You think this spot would be good for (.*)(\.)': specLine,
            'You are done speculating.': speculateDone,
            'You have found a vein of (.*)!': speculateDoublecheck,
            'You can\'t carry that many items.': 'drop all.pound\ndrop all.bundle',
            'You are done smithing .*': smith,
            'You are done carving .*.': smith,
            'You mess up smithing .*': failSmithing,
            'You mess up carving .*': failSmithing,
            'Your speculate attempt failed.': speculateFailed,
            'You are done skinning and butchering the body of .*': 'butcher corpse',
            }

    def honeTimer(self, mud):
        if 'honeSkills' not in mud.state:
            mud.state['honeSkills'] = ['constr title foo', 'gemdig', 'masonry title blarg', 'search', 'mastermine']
        
        skillToCmd = ['Construction', 'Gem Digging', 'Masonry', 'Searching', 'Master Mining']

        def onHoneSuccess(skill):
            skills = mud.state['honeSkills']
            if mud.state['honeMultiple'] < len(skills):
                cmd = skills[mud.state['honeMultiple']]
                mud.state['honing'] = (cmd, 1)
                mud.send(cmd)
                if skill in mud.state['skillLevels'] and mud.state['skillLevels'][skill] >= 99 and skill in skillToCmd:
                    mud.log("Removing " + skill + " from hone list")
                    del mud.state['honeSkills'][skillToCmd.index(skill)]
            else:
                mud.setTimerRemaining('hone', 301)
                mud.send('sleep')
            mud.state['honeMultiple'] += 1

        mud.state['honeMultiple'] = 0
        cmd = 'dye diaper red'
        # mud.state['hone_on_success'] = lambda: [mud.setTimerRemaining('hone', 305), mud.send('leep')]
        mud.state['hone_on_success'] = onHoneSuccess
        mud.state['honing'] = (cmd, 1)
        self.send("stand\n{}".format(cmd))
        
    def getTimers(self):
        if False:
            return {
                "hone": self.mktimer(60*5 + 5, self.honeTimer),
                }
        else:
            return {}

def getClass():
    return AutoSmith
