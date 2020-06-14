from modules.basemodule import BaseModule

import random
import re
import time


# start with at least 10 charisma, max int and wis
# At level 1, train scholar, practice write
# At level 2, write book
# At level 3, gain engraving and embroidering, prac herbology
# At level 4, gain combat log
#(# At level 5, gain organizing)
# At level 7, gain find home
# At level 9, gain wilderness lore
# At level 11, gain book naming
# At level 13, gain find ship
# At level 14, gain make maps
# At level 16, gain plant lore
# At level 22, gain planar lore
# At level 30, gain master herbology

spells_by_level = {
        1: ['herb herb'],
        2: ['label book', 'engrave bowl bowl', 'embroider belt belt'],
        3: ['light fire', 'combatlog self', 'combatlog stop'],
        4: ['organ room name'],
        # 5: ['smokesig testing testing 1 2 3'],
        6: ['entitle book book', 'findhome'],
        7: ['bookedit book', 'knowplant herb'],
        9: ['wlore', 'transcribe paper book'],
        10: ['bname book 1 book', 'speculate'],
        11: ['lore book'],
        12: ['rlore human', 'findship'],
        13: ['cwrite book', 'map paper'],
        15: ['plantlore'],
        18: ['recollect happy'],
        21: ['plore astral'],
        22: ['survey room book'],
        29: ['mherb herb'],
        }

def practiceOne(mud):
    level = mud.level() - 1
    mud.log("practiceOne")
    practiceImpl(mud, level, 9, -1)

def practiceTwo(mud):
    mud.log("practiceTwo")
    practiceImpl(mud, 9, 0, -1)

def practiceImpl(mud, begin, end, step):
    if mud.gmcp['room']['info']['num'] != 1741703288:
        mud.log("Not running Scholar script - must be in Pecking Place")
        return

    out = []
    for i in range(begin, end, step):
        if i in spells_by_level:
            for skill in spells_by_level[i]:
                out.append(skill)

    # don't wake when too low-level to actually do anything
    if out:
        mud.send("sta")
        for elem in out:
            mud.send(elem)
        mud.send("sleep")

    return


class Mage(BaseModule):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def getAliases(self):
        return {
                'spellup': self.spellUp,
                }

    def cast(self, spell):
        if ' ' in spell:
            spell = '"{spell}"'.format(spell=spell)
        self.send("cast " + spell)

    def wearOff(self, spell):
        if 'wantSpells' not in self.world.state:
            self.world.state['wantSpells'] = set()
        self.world.state['wantSpells'].add(spell)
        cast(spell)
        self.log(spell + " wore off")

    def wearOn(self, spell):
        if 'wantSpells' not in self.world.state:
            self.world.state['wantSpells'] = set()
        if spell in self.world.state['wantSpells']:
            self.world.state['wantSpells'].remove(spell)
        self.log(spell + " is active")

    def spellFail(self, spell):
        if 'wantSpells' not in self.world.state:
            self.world.state['wantSpells'] = set()
        self.log(spell + " failed")
        self.world.state['wantSpells'].add(spell)
        # delay?
        # self.send('cast "{spell}"'.format(spell=spell))

    def spellUp(self, mud=None, groups=None):
        if 'wantSpells' not in self.world.state:
            self.world.state['wantSpells'] = set()
        for spell in self.world.state['wantSpells']:
            self.cast(spell)

    def onMaxMana(self):
        self.send('stand')
        self.spellUp()

        if self.world.gmcp['room']['info']['num'] != 1741703288:
            self.log("Not running Mage script - must be in Grumpy Grotto")
            return

    def getTriggers(self):
        return {
                'You speak quickly to yourself, but nothing more happens.': lambda mud, groups: self.spellFail('haste'),
                'You attempt to invoke magical protection, but fail.': lambda mud, groups: self.spellFail('mage armor'),
                'You attempt to invoke an anti-magic globe, but fail.': lambda mud, groups: self.spellFail('globe'),
                'You speak reflectively, but nothing more happens.': lambda mud, groups: self.spellFail('mirror'),

                'You watch your skin turn hard as stone!': lambda mud, groups: self.wearOn('stoneskin'),
                'You invoke a magical glowing breast plate!': lambda mud, groups: self.wearOn('mage armor'),
                'You incant the reflective spell of you, and suddenly 3 copies appear.': lambda mud, groups: self.wearOn('mirror'),
		'You attempt to invoke an anti-magic globe, but fail.': lambda mud, groups: self.wearOn('globe'),

                'Your magical armor fades away.': lambda mud, groups: self.wearOff('mage armor'),
                'Your skin softens.': lambda mud, groups: self.wearOff('stoneskin'),
                'Your minor anti-magic globe fades.': lambda mud, groups: self.wearOff('globe'),

            '^You have 64 points remaining.': 'wis 15\nint 15\ncha 7\ncon 15\nstr 12\n ',
            '^Please choose from the following Classes:': 'mage',
            '^Is Mage correct': 'y',
            '^You have remorted back to level 1!': 'run n w\ntrain int\ntrain int\ntrain int\ntrain int',
            'You are hungry.': 'eat bread',
            'You are thirsty.': 'drink buffalo',
            r'(Grumpy|Grumpier|Grumpiest) wants to teach you .*\.  Is this Ok .y.N..': 'y',
            }

    def getTimers(self):
        return { }
                # "practiceOne": (False, 5+2*600, 60, practiceOne),
                # "practiceTwo": (False, 5+1*600, 615, practiceTwo),
                # "write": (False, 605, 15, write),
                # }

def getClass():
    return Mage
