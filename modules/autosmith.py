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
        90: 197,
        89: 194,
        88: 191,
        87: 189,
        86: 186,
        85: 183,
        84: 181,
        83: 179,
        82: 177,
        81: 174,
        80: 171,
        79: 168,
        78: 166,
        77: 163,
        76: 161,
        75: 157,
        74: 154,
        73: 151,
        72: 148,
        71: 146,
        70: 144,
        69: 141,
        68: 140,
        67: 138,
        66: 135,
        65: 133,
        64: 130,
        63: 128,
        62: 126,
        61: 122,
        60: 119,
        59: 116,
        58: 112,
        57: 109,
        }

marm_skills = [
        # TODO: filter out mithril and other special reqs. Don't forget to update marm_by_level.
        "oops index should be zero based",
        "Spiked Banded Armbands", # 12 15
        "Spiked Banded Vest", # 13 30
        "Spiked Banded Sleeves", # 14 15
        "Spiked Banded Handguards", # 14 5
        "Spiked Banded Vambrace", # 14 3
        "Spiked Banded Leggings", # 15 15
        "Spiked Banded Shirt", # 16 30
        "Spiked Banded Rearbraces", # 16 15
        "Spiked Banded Mitts", # 16 5
        "Spiked Banded Bracer", # 16 3
        "Spiked Banded Greaves", # 17 15
        "Spiked Banded Boots", # 17 10
        "Spiked Banded Mantle", # 17 5
        "Spiked Banded Skirt", # 18 15
        "Spiked Banded Pauldrons", # 18 15
        "PickelHaube", # 18 10
        "Spiked Banded Sabotons", # 18 10
        "Spiked Banded Gauntlets", # 18 5
        "Spiked Banded Girdle", # 18 5
        "Spiked Banded Lowerarm Cannon", # 18 3
        "Spiked Banded Jerkin", # 19 30
        "Spiked Banded Leg Cannons", # 19 15
        "Spiked Banded Collar", # 19 5
        "Spiked Banded Upperarm Cannons", # 20 15
        "spiked buckler", # 27 8
        "Embossed Fullplate Mantle", # 29 5
        "embossed plate cuirass", # 30 30
        "Embossed Fullplate Rearbraces", # 30 15
        "Embossed Fullplate Leggings", # 30 15
        "Embossed Fullplate Bracer", # 30 3
        "Casque", # 31 10
        "lantern shield", # 31 8
        "Embossed Fullplate Gauntlets", # 31 5
        "Embossed Fullplate Pauldrons", # 32 15
        "Morion", # 32 10
        "Embossed Fullplate Vambrace", # 32 3
        "Embossed Fullplate Girdle", # 33 5
        "Embossed Fullplate Locking Gauntlets", # 33 5
        "embossed chanfron", # 34 40
        "Do-Maru", # 34 30
        "Dwarven Plate Armbands", # 34 15
        "Embossed Fullplate Sabotons", # 35 10
        "Dwarven Plate Helm", # 35 10
        "Dwarven Plate Collar", # 35 5
        "Dwarven Plate Skirt", # 36 15
        "Dwarven Plate Boots", # 36 10
        "Cabasset", # 36 10
        "Beavered-Helm", # 37 10
        "Dwarven Plate Gauntlets", # 37 5
        "Dwarven Plate Girdle", # 37 5
        "Dwarven Plate Lowerarm Cannon", # 38 3
        "dwarven plate chanfron", # 39 40
        "Dwarven Plate Jerkin", # 39 30
        "Dwarven Plate Leg Cannons", # 39 15
        "Dwarven Plate Gorget", # 39 5
        "Dwarven Plate Upperarm Cannons", # 40 15
        "parma", # 40 15
        "Featherweight Chainmail Mantle", # 40 3
        "Steam-Powered Plate Mantle", # 41 5
        "Featherweight Chainmail Gloves", # 41 3
        "Featherweight Chainmail Cuffs", # 41 2
        "Featherweight Chainmail Shirt", # 42 15
        "Featherweight Chainmail Sleeves", # 42 8
        "Featherweight Chainmail Leggings", # 42 8
        "Hara-Ate", # 43 30
        "Featherweight Chainmail Socks", # 43 5
        "Featherweight Chainmail Coif", # 43 5
        "Featherweight Chainmail Collar", # 43 3
        "Featherweight Chainmail Jacket", # 44 23
        "Featherweight Chainmail Vest", # 44 15
        "Galeo", # 44 10
        "Steam-Powered Plate Vest", # 45 30
        "Legionary Helmet", # 45 10
        "Steam-Powered Plate Pauldrons", # 46 15
        "Steam-Powered Plate Boots", # 46 10
        "Featherweight Chainmail Skirt", # 46 8
        "Featherweight Chainmail Coat", # 47 23
        "Steam-Powered Plate Gauntlets", # 47 5
        "Featherweight Chainmail Belt", # 47 3
        "Doublemail Mantle", # 48 5
        "Steam-Powered Plate Lowerarm Cannon", # 48 3
        "Featherweight Chainmail Hauberk", # 49 23
        "Steam-Powered Plate Leg Cannons", # 49 15
        "Featherweight Chainmail Jerkin", # 49 15
        "featherweight chainmail chanfron", # 50 40
        "Steam-Powered Plate Upperarm Cannons", # 50 15
        "fayum", # 50 15
        "Haramaki-Do", # 51 30
        "Haidate", # 51 15
        "manica lamminata", # 51 3
        "lorica hamata", # 52 30
        "Mempo", # 52 5
        "Ude-Ate", # 52 3
        "Sode", # 53 15
        "ocreae", # 53 15
        "Armet", # 53 10
        "Steam-Powered Plate Girdle", # 53 5
        "lorica squamata", # 54 30
        "coolus helmet", # 54 10
        "kogake", # 54 10
        "Kote", # 54 3
        "kabuto", # 55 10
        "Yugake", # 55 5
        "lorica muscalata", # 56 30
        "pteruges", # 56 15
        "Wakibiki", # 56 5
        "scutum", # 57 15
        "Battleplate Mantle", # 57 5
        "Doublemail Gloves", # 57 5
        "Battleplate Armbands", # 58 15
        "Battleplate Leggings", # 58 15
        "Doublemail Cuffs", # 58 3
        "Doublemail Shirt", # 59 30
        "Battleplate Sleeves", # 59 15
        "Doublemail Leggings", # 59 15
        "Doublemail Belt", # 59 5
        "Doublemail Sleeves", # 60 15
        "Battleplate Handguards", # 60 5
        "Battleplate Bracer", # 60 3
        "Battleplate Greaves", # 61 15
        "Doublemail Socks", # 61 10
        "Doublemail Collar", # 61 5
        "Battleplate Rearbraces", # 62 15
        "Doublemail Coif", # 62 10
        "Battleplate Collar", # 62 5
        "Battleplate Mitts", # 62 5
        "Battleplate Vest", # 63 30
        "Mirmillo", # 63 10
        "Dragon helm", # 64 10
        "Battleplate Vambrace", # 64 3
        "Battleplate Pauldrons", # 65 15
        "Battleplate Boots", # 65 10
        "Battleplate Gauntlets", # 65 5
        "Doublemail Vest", # 66 30
        "Doublemail Skirt", # 66 15
        "Battleplate Skirt", # 67 15
        "Battleplate Girdle", # 67 5
        "Battleplate Lowerarm Cannon", # 67 3
        "Doublemail Jerkin", # 68 30
        "Battleplate Leg Cannons", # 68 15
        "Battleplate Jerkin", # 69 30
        "battleplate chanfron", # 70 40
        "Battleplate Upperarm Cannons", # 70 15
        "Battleplate Locking Gauntlets", # 70 5
        "jousting shield", # 71 15
        "Ancient Mantle", # 71 5
        "Ancient Armbands", # 72 15
        "Battleplate Sabotons", # 72 10
        "Ancient Sleeves", # 73 15
        "Ancient Leggings", # 73 15
        "Ancient Handguards", # 73 5
        "Ancient Greaves", # 74 15
        "Ancient Collar", # 74 5
        "Ancient Bracer", # 74 3
        "Ancient Socks", # 75 10
        "Ancient Helmet", # 75 10
        "Ancient Mitts", # 75 5
        "Ancient Vest", # 76 30
        "Ancient Rearbraces", # 76 15
        "Demon helm", # 76 10
        "Ancient Vambrace", # 76 3
        "Ancient Boots", # 77 10
        "montefortino helmet", # 77 10
        "Ancient Skirt", # 78 15
        "Ancient Gauntlets", # 78 5
        "Ancient Girdle", # 78 5
        "Ancient Pauldrons", # 79 15
        "Ancient Lowerarm Cannon", # 79 3
        "Ancient Jerkin", # 80 30
        "Ancient Upperarm Cannons", # 80 15
        "Ancient Leg Cannons", # 80 15
        "ancient chanfron", # 81 40
        "war-door", # 81 15
        "Ancient Locking Gauntlets", # 81 5
        "Demonic Armbands", # 82 15
        "Ancient Sabotons", # 82 10
        "Sacred Mantle", # 82 5
        "Sacred Shirt", # 83 30
        "Demonic Leggings", # 83 15
        "Demonic Gauntlets", # 84 5
        "Demonic Bracer", # 84 3
        "imperial helmet", # 85 10
        "Demonic Collar", # 85 5
        "Sacred Crown", # 86 10
        "Sacred Gauntlets", # 86 5
        "Sacred Vambrace", # 86 3
        "pavise", # 87 15
        "Sacred Skirt", # 87 15
        "Demonic Boots", # 87 10
        "Sacred Boots", # 88 10
        "Demonic Locking Gauntlets", # 88 5
        "Demonic Jerkin", # 89 30
        "Demonic Girdle", # 89 5
        "Sacred Locking Gauntlets", # 89 5
        "Demonic Hauberk", # 90 45
        "Sacred Pauldrons", # 90 15
        "Sacred Girdle", # 90 5
        "sacred chanfron", # 91 40
        "demonic chanfron", # 91 40
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


# unused
lweap_skills = [
        "legendary butter knife", # 60 1
        "legendary club", # 61 12
        "legendary spear", # 61 12
        "legendary khopesh", # 61 10
        "legendary mallet", # 61 8
        "legendary throwing iron", # 61 2
        "legendary staff", # 62 15
        "legendary tulwar", # 62 14
        "legendary flail", # 62 12
        "legendary hand ax", # 62 8
        "legendary knife", # 62 2
        "legendary shillelagh", # 63 8
        "legendary sickle", # 63 8
        "legendary machete", # 63 6
        "legendary throwing knife", # 63 2
        "legendary large axe", # 64 18
        "legendary sai", # 64 5
        "legendary throwing axe", # 64 4
        "legendary chefs knife", # 64 3
        "legendary glaive", # 65 22
        "legendary orc blade", # 65 16
        "legendary short sword", # 65 10
        "legendary boomerang", # 65 4
        "legendary halberd", # 66 24
        "legendary flamberge", # 66 24
        "legendary two-headed flail", # 66 15
        "legendary hatchet", # 66 8
        "legendary nunchaku", # 66 8
        "legendary dagger", # 66 6
        "legendary broad axe", # 67 22
        "legendary military fork", # 67 18
        "legendary sceptre", # 67 12
        "legendary short staff", # 67 10
        "legendary long sword", # 67 10
        "legendary foil", # 67 2
        "legendary maul", # 68 30
        "legendary axe", # 68 10
        "legendary cutlass", # 68 8
        "legendary serrated knife", # 68 4
        "legendary craftsmans hammer", # 68 4
        "legendary shuriken", # 68 2
        "legendary spiked club", # 69 15
        "legendary yari", # 69 14
        "legendary gladius", # 69 10
        "legendary wakizashi", # 69 10
        "legendary giant axe", # 70 50
        "legendary fauchard", # 70 24
        "legendary two-handed club", # 70 20
        "legendary claymore", # 70 14
        "legendary gnout", # 70 12
        "legendary poignard", # 70 7
        "legendary bill-guisarme", # 71 28
        "legendary long staff", # 71 16
        "legendary kama", # 71 6
        "legendary epee", # 71 6
        "legendary dart", # 71 1
        "legendary bardiche", # 72 36
        "legendary giant sword", # 72 30
        "legendary kusari-gama", # 72 12
        "legendary tomahawk", # 72 6
        "legendary dirk", # 72 5
        "legendary sledgehammer", # 73 40
        "legendary light lance", # 73 16
        "legendary mace", # 73 12
        "legendary rapier", # 73 6
        "legendary throwing hammer", # 73 4
        "legendary chain", # 74 25
        "legendary double axe", # 74 16
        "legendary crys-knife", # 74 6
        "legendary great axe", # 75 27
        "legendary voulge", # 75 18
        "legendary morning star", # 75 16
        "legendary bastard sword", # 75 14
        "legendary partisan", # 76 26
        "legendary military pick", # 76 11
        "legendary jewelers hammer", # 76 3
        "legendary throwing spike", # 76 1
        "legendary cudgel", # 77 14
        "legendary quarterstaff", # 77 12
        "legendary shamshir", # 77 12
        "legendary weighted axe", # 77 6
        "legendary great maul", # 78 50
        "legendary pike", # 78 20
        "legendary twohanded sword", # 78 20
        "legendary tabar", # 78 18
        "legendary scourge", # 78 10
        "legendary rondel", # 78 6
        "legendary kyoketsu-shogi", # 78 6
        "legendary grand sceptre", # 79 16
        "legendary falchion", # 79 12
        "legendary katar", # 79 8
        "legendary herculean club", # 80 30
        "legendary heavy lance", # 80 30
        "legendary battle dart", # 80 1
        "legendary battle axe", # 81 25
        "legendary jo staff", # 81 8
        "legendary drussus", # 81 8
        "legendary manriki-gusari", # 81 3
        "legendary barbed whip", # 82 18
        "legendary crowbill", # 82 14
        "legendary stiletto", # 82 10
        "legendary hammer", # 82 10
        "legendary javelin", # 82 8
        "legendary martel de fer", # 83 40
        "legendary trident", # 83 22
        "legendary scimitar", # 83 16
        "legendary flanged mace", # 83 14
        "legendary bec de corbin", # 84 22
        "legendary no-dachi", # 84 20
        "legendary three-sectioned staff", # 84 15
        "legendary bearded axe", # 85 20
        "legendary jitte", # 85 5
        "legendary pixie blade", # 85 3
        "legendary ranseur", # 86 30
        "legendary war axe", # 86 14
        "legendary cat-o-nine tails", # 86 14
        "legendary weighted knife", # 86 2
        "legendary bo staff", # 87 14
        "legendary cat claws", # 87 10
        "legendary katana", # 87 10
        "legendary pilum", # 87 8
        "legendary scythe", # 88 20
        "legendary war sceptre", # 88 18
        "legendary lucern hammer", # 88 18
        "legendary main gauche", # 88 4
        "legendary executioners axe", # 89 20
        "legendary warhammer", # 89 12
        "legendary sabre", # 89 8
        "legendary dwarven thrower", # 89 4
        "legendary naginata", # 90 35
        "legendary half-moon", # 90 25
        "legendary zweihander", # 90 24
        "legendary three-headed flail", # 90 18
        "legendary hurlbat", # 90 8
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


class AutoSmith(BaseModule):
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
    return AutoSmith
