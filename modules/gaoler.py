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
    mud.send('run s e 4s w 2s e 2n')
    mud.send('unlock w')
    mud.send('open w')
    mud.send('w')
    mud.send('lock e')
    mud.send('speculate')


mweap_by_level = {
        31: 0,
        32: 8,
        33: 13,
        34: 19,
        35: 24,
        36: 34,
        37: 38,
        38: 44,
        39: 50,
        40: 58,
        41: 61,
        42: 70,
        43: 75,
        44: 81,
        45: 85,
        46: 92,
        47: 95,
        48: 100,
        49: 105,
        50: 110,
        51: 114,
        52: 118,
        53: 121,
        54: 124,
        55: 126,
        56: 130,
        57: 131
        }

mweap_skills = [
        "Master Butter Knife",
        "Master Sai",
        "Master Mallet",
        "Master Shillelagh",
        "Master Sickle",
        "Master Short Staff",
        "Master Khopesh",
        "Master Spear",
        "Master Knife",
        "Master Craftsmans Hammer",
        "Master Boomerang",
        "Master Club",
        "Master Tulwar",
        "Master Throwing Iron",
        "Master Throwing Knife",
        "Master Chefs Knife",
        "Master Machete",
        "Master Hand ax",
        "Master Throwing Hammer",
        "Master Dagger",
        "Master Flail",
        "Master Cudgel",
        "Master Double Axe",
        "Master Glaive",
        "Master Dart",
        "Master Jewelers Hammer",
        "Master Serrated Knife",
        "Master Throwing Spike",
        "Master Manriki-Gusari",
        "Master Short Sword",
        "Master Military Pick",
        "Master Long Staff",
        "Master Orc Blade",
        "Master Flamberge",
        "Master Foil",
        "Master Poignard",
        "Master Axe",
        "Master Halberd",
        "Master Pixie Blade",
        "Master Dirk",
        "Master Hammer",
        "Master Morning Star",
        "Master Military Fork",
        "Master Long Sword",
        "Master Balanced Knife",
        "Master Battle Dart",
        "Master Throwing Axe",
        "Master Hatchet",
        "Master Warhammer",
        "Master Yari",
        "Master Kama",
        "Master Cutlass",
        "Master Katar",
        "Master Gladius",
        "Master Scourge",
        "Master Wakizashi",
        "Master QuarterStaff",
        "Master Spiked Club",
        "Master Large Axe",
        "Master Fauchard",
        "Master Maul",
        "Master Shuriken",
        "Master Epee",
        "Master Kyoketsu-Shogi",
        "Master Rapier",
        "Master Tomahawk",
        "Master Jo Staff",
        "Master Cat Claws",
        "Master Claymore",
        "Master Bill-guisarme",
        "Master Nunchaku",
        "Master Shamshir",
        "Master Crowbill",
        "Master Bastard Sword",
        "Master Bardiche",
        "Master Balanced Axe",
        "Master Crys-knife",
        "Master Javelin",
        "Master Three-sectioned staff",
        "Master Broad Axe",
        "Master Great Maul",
        "Master Falchion",
        "Master Gnout",
        "Master Light Lance",
        "Master Barbed Whip",
        "Master Rondel",
        "Master Drussus",
        "Master Mace",
        "Master War Axe",
        "Master Scimitar",
        "Master Chain",
        "Master Giant Sword",
        "Master Pilum",
        "Master Stiletto",
        "Master Giant Axe",
        "Master Bo Staff",
        "Master Two-headed Flail",
        "Master Three-headed Flail",
        "Master Voulge",
        "Master Great Axe",
        "Master Main Gauche",
        "Master Hurlbat",
        "Master Cat-o-nine tails",
        "Master Tabar",
        "Master Partisan",
        "Master Dwarven Thrower",
        "Master Katana",
        "Master Pike",
        "Master Herculean Club",
        "Master Sledgehammer",
        "Master Kusari-Gama",
        "Master Grand Sceptre",
        "Master Battle Axe",
        "Master Heavy Lance",
        "Master Sabre",
        "Master Flanged Mace",
        "Master Trident",
        "Master Martel de Fer",
        "Master Lucern Hammer",
        "Master Bec de Corbin",
        "Master Half-moon",
        "Master Jitte",
        "Master Bearded Axe",
        "Master Ranseur",
        "Master Scythe",
        "Master No-Dachi",
        "Master War Sceptre",
        "Master Executioners Axe",
        "Master Naginata",
        "Master Zweihander",
        "Master Sceptre",
        "Master TwoHanded Sword",
    ]

def skill_by_level(lvl):
    if 31 <= lvl:
        return 'mweap', mweap_by_level, mweap_skills

def smith(mud, _):
    if 'smithing' in mud.state:
        ptr = mud.state['smithing']
        skill, _, arg_by_ptr = skill_by_level(mud.level())
        return "{skill} {arg}".format(skill=skill, arg=arg_by_ptr[ptr])
        mud.state['smithing'] = ptr - 1

def startSmithing(mud, _):
    level = mud.level()
    _, ptr_by_level, _ = skill_by_level(level)
    mud.state['smithing'] = ptr_by_level[level]
    return smith(mud, _)


class Gaoler(BaseModule):
    def getAliases(self):
        return {
                'smith': startSmithing,
                }

    def getTriggers(self):
        return {
            'You are thirsty.': 'drink sink',
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
            'You are done speculating.': 'speculate',
            'You can\'t carry that many items.': 'drop all.pound\ndrop all.bundle',
            'You are done smithing .*': smith,
            }

    def getTimers(self):
        return {
                # "hone": self.mktimer(60*5 + 5, lambda: self.send("irrig title On a pond\nexcav title On a pond\nlandscap title On a pond\nrun 2e\nmarm Spiked Banded Handguards\nrun 2w\nmasterfish\nspeculate"))
                }

def getClass():
    return Gaoler
