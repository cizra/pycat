from modules.basemodule import BaseModule

import random
import re
import time


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


marm_by_level = {
        57: 21,
        58: 27,
        59: 27,
        60: 29,
        61: 31,
        62: 31,
        63: 31,
        64: 31,
        65: 31,
        66: 31,
        67: 56,
        68: 56,
        69: 56,
        70: 56,
        71: 56,
        72: 56,
        73: 56,
        74: 56,
        75: 56,
        76: 56,
        77: 90,
        78: 97,
        79: 97,
        80: 97,
        81: 100,
        82: 100,
        83: 100,
        84: 100,
        85: 100,
        86: 100,
        87: 112,
        88: 112,
        89: 112,
        90: 112,
        91: 112,
        }

marm_skills = [
        "Hara-Ate",  # 57 84
        "Sode",  # 57 42
        "Haidate",  # 57 42
        "Legionary Helmet",  # 57 28
        "Mempo",  # 57 28
        "Sune-Ate",  # 57 28
        "Doublemail Socks",  # 57 28
        "Galeo",  # 57 28
        "Battleplate Greaves",  # 57 28
        "Battleplate Sabottons",  # 57 28
        "Kabuto",  # 57 28
        "Mirmillo",  # 57 28
        "Yugake",  # 57 14
        "Wakibiki",  # 57 14
        "Doublemail Gloves",  # 57 14
        "Doublemail Collar",  # 57 14
        "Doublemail Mantle",  # 57 14
        "Battleplate Gauntlets",  # 57 14
        "Battleplate Handguards",  # 57 14
        "Battleplate Collar",  # 57 14
        "Battleplate Mantle",  # 57 14
        "Battleplate Mitts",  # 57 14
        "Battleplate Boots",  # 58 28
        "Kote",  # 58 14
        "Doublemail Cuffs",  # 58 14
        "Battleplate Bracer",  # 58 14
        "Battleplate Vambrace",  # 58 14
        "Battleplate Lowerarm Cannon",  # 58 14
        "Lorica Segmenta",  # 60 63
        "Battleplate Locking Gauntlets",  # 60 14
        "Doublemail Belt",  # 61 14
        "Battleplate Girdle",  # 61 14
        "Doublemail Jacket",  # 67 135
        "Battleplate Hauberk",  # 67 135
        "Haramaki-Do",  # 67 90
        "Doublemail Shirt",  # 67 90
        "Doublemail Jerkin",  # 67 90
        "Doublemail Vest",  # 67 90
        "Battleplate Jerkin",  # 67 90
        "Battleplate Vest",  # 67 90
        "Doublemail Sleeves",  # 67 45
        "Doublemail Leggings",  # 67 45
        "Doublemail Skirt",  # 67 45
        "Battleplate Sleeves",  # 67 45
        "Battleplate Rearbraces",  # 67 45
        "Battleplate Upperarm Cannons ",  # 67 45
        "Battleplate Pauldrons",  # 67 45
        "Battleplate Leggings",  # 67 45
        "Battleplate Leg Cannons",  # 67 45
        "Battleplate Armbands",  # 67 45
        "Battleplate Skirt",  # 67 45
        "Doublemail Coif",  # 67 30
        "Dragon helm",  # 67 30
        "Doublemail Coat",  # 67 13
        "Doublemail Hauberk",  # 67 13
        "Battleplate Coat",  # 67 13
        "Battleplate Jacket",  # 67 13
        "Demon Armor",  # 77 510
        "Ancient Coat",  # 77 144
        "Ancient Hauberk",  # 77 144
        "Do-Maru",  # 77 96
        "Ancient Vest",  # 77 96
        "Ancient Jerkin",  # 77 96
        "Hallowed Vestments",  # 77 51
        "Ancient Sleeves",  # 77 48
        "Ancient Rearbraces",  # 77 48
        "Ancient Upperarm Cannons",  # 77 48
        "Ancient Pauldrons",  # 77 48
        "Ancient Leggings",  # 77 48
        "Ancient Leg Cannons",  # 77 48
        "Ancient Armbands",  # 77 48
        "Ancient Skirt",  # 77 48
        "Ancient Helmet",  # 77 32
        "Casque",  # 77 32
        "Ancient Socks",  # 77 32
        "Ancient Greaves",  # 77 32
        "Ancient Sabottons",  # 77 32
        "Demonic Greaves",  # 77 32
        "Ancient Gauntlets",  # 77 16
        "Ancient Locking Gauntlets",  # 77 16
        "Ancient Handguards",  # 77 16
        "Demonic Gauntlets",  # 77 16
        "Demonic Locking Gauntlets",  # 77 16
        "Sacred Gauntlets",  # 77 16
        "Sacred Locking Gauntlets",  # 77 16
        "Ancient Collar",  # 77 16
        "Ancient Mantle",  # 77 16
        "Demonic Collar",  # 77 16
        "Sacred Mantle",  # 77 16
        "Ancient Mitts",  # 77 16
        "Ancient Jacket",  # 77 14
        "Ancient Boots",  # 78 32
        "Sacred Boots",  # 78 32
        "Ancient Bracer",  # 78 16
        "Ancient Vambrace",  # 78 16
        "Ancient Lowerarm Cannon",  # 78 16
        "Demonic Bracer",  # 78 16
        "Sacred Vambrace",  # 78 16
        "Ancient Girdle",  # 81 16
        "Demonic Girdle",  # 81 16
        "Sacred Girdle",  # 81 16
        "Demonic Coat",  # 87 153
        "Sacred Jacket",  # 87 153
        "Sacred Shirt",  # 87 102
        "Demonic Armbands",  # 87 51
        "Sacred Pauldrons",  # 87 51
        "Demonic Leggings",  # 87 51
        "Sacred Skirt",  # 87 51
        "Demon helm",  # 87 34
        "Sacred Crown",  # 87 34
        "Sacred Armament",  # 87 15
        "Demonic Hauberk",  # 87 15
        "Demonic Jerkin",  # 87 10
]

mweap_by_level = {
        31: 7,
        32: 12,
        33: 18,
        34: 23,
        35: 33,
        36: 37,
        37: 43,
        38: 49,
        39: 57,
        40: 60,
        41: 69,
        42: 74,
        43: 80,
        44: 84,
        45: 91,
        46: 94,
        47: 99,
        48: 104,
        49: 109,
        50: 113,
        51: 117,
        52: 120,
        53: 123,
        54: 125,
        55: 129,
        56: 130,
        57: 131
        }

mweap_skills = [
        "Master Spear",
        "Master Khopesh",
        "Master Short Staff",
        "Master Sickle",
        "Master Shillelagh",
        "Master Mallet",
        "Master Sai",
        "Master Butter Knife",
        "Master Tulwar",
        "Master Club",
        "Master Boomerang",
        "Master Craftsmans Hammer",
        "Master Knife",
        "Master Throwing Hammer",
        "Master Hand ax",
        "Master Machete",
        "Master Chefs Knife",
        "Master Throwing Knife",
        "Master Throwing Iron",
        "Master Glaive",
        "Master Double Axe",
        "Master Cudgel",
        "Master Flail",
        "Master Dagger",
        "Master Flamberge",
        "Master Orc Blade",
        "Master Long Staff",
        "Master Military Pick",
        "Master Short Sword",
        "Master Manriki-Gusari",
        "Master Throwing Spike",
        "Master Serrated Knife",
        "Master Jewelers Hammer",
        "Master Dart",
        "Master Halberd",
        "Master Axe",
        "Master Poignard",
        "Master Foil",
        "Master Long Sword",
        "Master Military Fork",
        "Master Morning Star",
        "Master Hammer",
        "Master Dirk",
        "Master Pixie Blade",
        "Master Yari",
        "Master Warhammer",
        "Master Hatchet",
        "Master Throwing Axe",
        "Master Battle Dart",
        "Master Balanced Knife",
        "Master Spiked Club",
        "Master QuarterStaff",
        "Master Wakizashi",
        "Master Scourge",
        "Master Gladius",
        "Master Katar",
        "Master Cutlass",
        "Master Kama",
        "Master Maul",
        "Master Fauchard",
        "Master Large Axe",
        "Master Bill-guisarme",
        "Master Claymore",
        "Master Cat Claws",
        "Master Jo Staff",
        "Master Tomahawk",
        "Master Rapier",
        "Master Kyoketsu-Shogi",
        "Master Epee",
        "Master Shuriken",
        "Master Bardiche",
        "Master Bastard Sword",
        "Master Crowbill",
        "Master Shamshir",
        "Master Nunchaku",
        "Master Great Maul",
        "Master Broad Axe",
        "Master Three-sectioned staff",
        "Master Javelin",
        "Master Crys-knife",
        "Master Balanced Axe",
        "Master Barbed Whip",
        "Master Light Lance",
        "Master Gnout",
        "Master Falchion",
        "Master Giant Sword",
        "Master Chain",
        "Master Scimitar",
        "Master War Axe",
        "Master Mace",
        "Master Drussus",
        "Master Rondel",
        "Master Giant Axe",
        "Master Stiletto",
        "Master Pilum",
        "Master Great Axe",
        "Master Voulge",
        "Master Three-headed Flail",
        "Master Two-headed Flail",
        "Master Bo Staff",
        "Master Partisan",
        "Master Tabar",
        "Master Cat-o-nine tails",
        "Master Hurlbat",
        "Master Main Gauche",
        "Master Sledgehammer",
        "Master Herculean Club",
        "Master Pike",
        "Master Katana",
        "Master Dwarven Thrower",
        "Master Heavy Lance",
        "Master Battle Axe",
        "Master Grand Sceptre",
        "Master Kusari-Gama",
        "Master Martel de Fer",
        "Master Trident",
        "Master Flanged Mace",
        "Master Sabre",
        "Master Half-moon",
        "Master Bec de Corbin",
        "Master Lucern Hammer",
        "Master Ranseur",
        "Master Bearded Axe",
        "Master Jitte",
        "Master No-Dachi",
        "Master Scythe",
        "Master Zweihander",
        "Master Naginata",
        "Master Executioners Axe",
        "Master War Sceptre",
        "Master Sceptre",
        "Master TwoHanded Sword",
    ]

def skill_by_level(lvl):
    if 31 <= lvl and lvl <= 57:
        return 'mweap', mweap_by_level, mweap_skills
    elif 57 < lvl:
        return 'marm', marm_by_level, marm_skills

def smith(mud, _):
    if 'task_start_time' in mud.state:
        mud.log("The task took {}s".format(time.time() - mud.state['task_start_time']))

    level = mud.level()
    skill, ptr_by_level, arg_by_ptr = skill_by_level(level)
    pbl = ptr_by_level[level] if level in ptr_by_level else list(ptr_by_level)[-1]
    if 'smithing' not in mud.state:
        mud.state['smithing'] = pbl + 1

    mud.state['smithing'] -= 1

    ptr = max(0, min(mud.state['smithing'], pbl))
    if pbl - ptr > 6:
        ptr = mud.state['smithing'] = pbl
    return "{skill} {arg}".format(skill=skill, arg=arg_by_ptr[ptr])

def failSmithing(mud, _):
    if 'smithing' in mud.state:
        mud.state['smithing'] += 1


def speculateFor(mud, groups):
    mud.state['speculate'] = {
            'direction': groups[0],
            'targets': groups[1].split(' '),
            'success': True,
            }
    mud.send("speculate")

def specLine(mud, groups):
    fixdir = {
            'below': 'd',
            'above you': 'u',
            'to the north': 'n',
            'to the east': 'e',
            'to the south': 's',
            'to the west': 'w',
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
                'silk': 'masterforage',
                }
        for tgt in mud.state['speculate']['targets']:
            if tgt in mud.state['speculate']['results']:
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

class Gaoler(BaseModule):
    def getAliases(self):
        return {
                'smith': smith,
                'specfor (.) (.*)': speculateFor,
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
            'There looks like (.*) (below|above you|to the north|to the east|to the south|to the west).': specLine,
            'You think this spot would be good for (.*)(). ': specLine,
            'You are done speculating.': speculateDone,
            'You have found a vein of (.*)!': speculateDoublecheck,
            'You can\'t carry that many items.': 'drop all.pound\ndrop all.bundle',
            'You are done smithing .*': smith,
            'You mess up smithing .*': failSmithing,
            'Your speculate attempt failed.': speculateFailed,
            'You are done skinning and butchering the body of .*': 'butcher corpse',
            }

    def getTimers(self):
        return {
                # "hone": self.mktimer(60*5 + 5, lambda: self.send("irrig title On a pond\nexcav title On a pond\nlandscap title On a pond\nrun 2e\nmarm Spiked Banded Handguards\nrun 2w\nmasterfish\nspeculate"))
                }

def getClass():
    return Gaoler
