from modules.basemodule import BaseModule

import random
import re
import time

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
        self.cast(spell)
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


    def getTriggers(self):
        return {
                'Your meditation is interrupted by the noise.': 'meditate',
                'You attempt to meditate, but lose concentration.': 'meditate',
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
