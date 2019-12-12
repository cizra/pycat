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
    mud.modules['mapper'].go(-420699692)
    mud.send('fill barrel sink\ndrink sink\ndrink sink\ns\ne\nforage')

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

carve_by_level = {
        28: 5,
        29: 6,
        30: 7,
        }

carve_skills = [
        "chopstick",
        "chopstick",
        "chopstick",
        "chopstick",
        "chopstick",
        "ceremonial dagger",
        "chest",
        "crib",
        ]

weap_by_level = {
        7: 48,
        8: 54,
        9: 61,
        10: 68,
        11: 75,
        12: 79,
        13: 84,
        14: 87,
        15: 94,
        16: 97,
        17: 103,
        18: 107,
        19: 112,
        20: 115,
        21: 119,
        22: 122,
        23: 125,
        24: 128,
        25: 131,
        26: 131,
        27: 131,
        28: 131,
        29: 131,
        30: 131,
        31: 131,
        }

weap_skills = [
      "Butter Knife",  # 0 1
      "Dizzy Boff Stick",  # 1 20
      "Club",  # 1 12
      "Spear",  # 1 12
      "Khopesh",  # 1 12
      "Short Staff",  # 1 10
      "Sickle",  # 1 8
      "Shillelagh",  # 1 8
      "Mallet",  # 1 8
      "Throwing Iron",  # 1 2
      "Throwing Knife",  # 1 2
      "Tulwar",  # 2 14
      "Nunchaku",  # 2 8
      "Boomerang",  # 2 8
      "Craftsmans Hammer",  # 2 4
      "Knife",  # 2 2
      "Hand ax",  # 3 8
      "Throwing Hammer",  # 3 8
      "Machete",  # 3 6
      "Sai",  # 3 5
      "Chefs Knife",  # 3 3
      "Glaive",  # 4 22
      "Double Axe",  # 4 16
      "Cudgel",  # 4 14
      "Flail",  # 4 12
      "Gnout",  # 4 12
      "Dagger",  # 4 6
      "Manriki-Gusari",  # 4 6
      "Flamberge",  # 5 36
      "Chain",  # 5 25
      "Long Staff",  # 5 16
      "Military Pick",  # 5 11
      "Short Sword",  # 5 10
      "Serrated Knife",  # 5 4
      "Throwing Spike",  # 5 4
      "Jewelers Hammer",  # 5 3
      "Dart",  # 5 2
      "Halberd",  # 6 24
      "Orc Blade",  # 6 16
      "Axe",  # 6 10
      "Poignard",  # 6 7
      "Long Sword",  # 7 20
      "Military Fork",  # 7 18
      "Morning Star",  # 7 16
      "Two-headed Flail",  # 7 15
      "Hammer",  # 7 10
      "Dirk",  # 7 5
      "Throwing Axe",  # 7 4
      "Foil",  # 7 2
      "Yari",  # 8 14
      "Warhammer",  # 8 12
      "Hatchet",  # 8 8
      "Cutlass",  # 8 8
      "Battle Dart",  # 8 4
      "Balanced Knife",  # 8 2
      "Spiked Club",  # 9 15
      "QuarterStaff",  # 9 12
      "Scourge",  # 9 10
      "Gladius",  # 9 10
      "Wakizashi",  # 9 10
      "Katar",  # 9 8
      "Kama",  # 9 6
      "Maul",  # 10 30
      "Claymore",  # 10 26
      "Fauchard",  # 10 24
      "Large Axe",  # 10 18
      "Kusari-Gama",  # 10 12
      "Cat Claws",  # 10 10
      "Epee",  # 10 6
      "Bill-guisarme",  # 11 28
      "Crowbill",  # 11 14
      "Jo Staff",  # 11 8
      "Kyoketsu-Shogi",  # 11 6
      "Rapier",  # 11 6
      "Tomahawk",  # 11 6
      "Shuriken",  # 11 2
      "Bardiche",  # 12 36
      "Bastard Sword",  # 12 24
      "Broad Axe",  # 12 22
      "Shamshir",  # 12 12
      "Great Maul",  # 13 50
      "Three-sectioned staff",  # 13 15
      "Javelin",  # 13 8
      "Crys-knife",  # 13 6
      "Balanced Axe",  # 13 6
      "butter knife",  # 14 18
      "Light Lance",  # 14 16
      "Falchion",  # 14 12
      "Giant Sword",  # 15 50
      "Scimitar",  # 15 16
      "War Axe",  # 15 14
      "Mace",  # 15 12
      "Sceptre",  # 15 12
      "Drussus",  # 15 8
      "Rondel",  # 15 6
      "Giant Axe",  # 16 50
      "Stiletto",  # 16 10
      "Pilum",  # 16 8
      "TwoHanded Sword",  # 17 30
      "Great Axe",  # 17 27
      "Three-headed Flail",  # 17 18
      "Voulge",  # 17 18
      "Bo Staff",  # 17 14
      "Pixie Blade",  # 17 3
      "Partisan",  # 18 26
      "Tabar",  # 18 18
      "Hurlbat",  # 18 8
      "Main Gauche",  # 18 4
      "Sledgehammer",  # 19 40
      "Herculean Club",  # 19 30
      "Pike",  # 19 20
      "Katana",  # 19 16
      "Cat-o-nine tails",  # 19 14
      "Heavy Lance",  # 20 30
      "Battle Axe",  # 20 25
      "Grand Sceptre",  # 20 16
      "Martel de Fer",  # 21 40
      "Trident",  # 21 22
      "Flanged Mace",  # 21 14
      "Sabre",  # 21 8
      "Half-moon",  # 22 25
      "Bec de Corbin",  # 22 22
      "Lucern Hammer",  # 22 18
      "Ranseur",  # 23 30
      "Bearded Axe",  # 23 20
      "Jitte",  # 23 5
      "No-Dachi",  # 24 30
      "Scythe",  # 24 20
      "War Sceptre",  # 24 18
      "Zweihander",  # 25 36
      "Naginata",  # 25 35
      "Executioners Axe",  # 25 25
        ]

marm_by_level = {
        28: 5,
        29: 5,
        30: 9,
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
        "embossed fullplate gauntlets",  # 23 10
        "embossed fullplate mantle",  # 23 10
        "embossed fullplate bracer",  # 24 10
        "embossed fullplate vambrace",  # 24 10
        "embossed fullplate locking gauntlets",  # 26 10
        "embossed fullplate girdle",  # 27 10
        "embossed fullplate leggings",  # 30 33
        "embossed fullplate pauldrons",  # 30 33
        "beavered-helm",  # 30 22
        "embossed fullplate rearbraces",  # 30 33
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
        "Doublemail Hauberk",  # 67 13
        "Doublemail Coat",  # 67 13
        "Battleplate Coat",  # 67 13
        "Battleplate Jacket",  # 67 13
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
        "Demon Armor",  # 77 510
        "Hallowed Vestments",  # 77 510
        "Ancient Coat",  # 77 144
        "Ancient Jacket",  # 77 144
        "Ancient Hauberk",  # 77 144
        "Do-Maru",  # 77 96 
        "Ancient Vest",  # 77 96 
        "Ancient Jerkin",  # 77 96 
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
        "Sacred Armament",  # 87 153
        "Demonic Hauberk",  # 87 153
        "Sacred Jacket",  # 87 153
        "Demonic Jerkin",  # 87 102
        "Sacred Shirt",  # 87 102
        "Demonic Armbands",  # 87 51 
        "Sacred Pauldrons",  # 87 51 
        "Demonic Leggings",  # 87 51 
        "Sacred Skirt",  # 87 51 
        "Demon helm",  # 87 34 
        "Sacred Crown",  # 87 34 
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
        "Master butter knife",
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
        "Master butter knife",
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
        "Master butter knife",
        "Master Hurlbat",
        "Master Main Gauche",
        "Master Sledgehammer",
        "Master Herculean Club",
        "Master Pike",
        "Master Katana",
        "Master butter knife",
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

armor_by_level = {
        26: 6,
        27: 7,
        28: 7,
        29: 7,
        30: 7,
        }

armor_skills = [
        "Fullplate Shirt",  # 23 60
        "Fullplate Boots",  # 24 20
        "Fullplate Bracer",  # 24 10
        "Fullplate Vambrace",  # 24 10
        "Fullplate Lowerarm Cannon",  # 24 10
        "Large Shield",  # 25 30
        "Fullplate Locking Gauntlets",  # 26 10
        "Fullplate Girdle",  # 27 10
]

black_by_level = {
        6: 6,
        7: 6,
        }

black_skills = [
        "cup",
        "cup",
        "cup",
        "cup",
        "trashcan",
        "hooded lantern",
        "lantern",
        ]

def skill_by_level(lvl):
    if lvl <= 7:
        return 'black supple', black_by_level, black_skills
    elif 8 <= lvl and lvl < 26:
        return 'weap agile', weap_by_level, weap_skills
        # return 's\narmors agile ringmail collar\narmors agile ringmail collar\narmors agile ringmail collar\narmors agile ringmail collar\narmors agile ringmail collar\nn\nweap agile', weap_by_level, weap_skills
    elif 26 <= lvl and lvl < 28:
        return 'armors agile', armor_by_level, armor_skills
    elif 28 <= lvl and lvl < 31:
        return 'marm agile', marm_by_level, marm_skills
    elif 31 <= lvl and lvl <= 57:
        return 'mweap agile', mweap_by_level, mweap_skills
    elif 57 < lvl:
        return 'marm agile', marm_by_level, marm_skills

def smith(mud, _):
    if 'task_start_time' in mud.state:
        mud.log("The task took {}s".format(time.time() - mud.state['task_start_time']))

    level = mud.level()
    skill, ptr_by_level, arg_by_ptr = skill_by_level(level)
    pbl = ptr_by_level[level] if level in ptr_by_level else list(ptr_by_level.keys())[-1]
    # print("level {} ptr_by_level {} list()[-1] {}, pbl {}".format(level, ptr_by_level, list(ptr_by_level.keys())[-1], pbl))
    if 'smithing' not in mud.state or mud.state['smithing'] > pbl:
        mud.state['smithing'] = pbl

    ptr = max(0, min(mud.state['smithing'], pbl))
    if pbl - mud.state['smithing'] > 6:
        ptr = mud.state['smithing'] = pbl
    mud.state['smithing'] -= 1
    # print("decr to {}".format(mud.state['smithing']))
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
    here = mud.gmcp['room']['info']['num']
    path = mud.modules['mapper'].path(-565511209)
    rpath = mud.modules['mapper'].path2(-565511209, here)
    return 'mastermine bundle all {resource}\nget {resource} bundle\n{path}\ndrink sink\ndrop {resource} bundle\nlook {resource} bundle\n{rpath}\nmastermine'.format(resource=resource, path=path, rpath=rpath)


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
            'A wood barrel is empty.': getWater,
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

    def getTimers(self):
        return {
                # "hone": self.mktimer(60*5 + 5, lambda: self.send("irrig title On a pond\nexcav title On a pond\nlandscap title On a pond\nrun 2e\nmarm Spiked Banded Handguards\nrun 2w\nmasterfish\nspeculate"))
                }

def getClass():
    return Gaoler
