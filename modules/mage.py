import random
import re
import time

from modules.basemodule import BaseModule
from modules.CoffeeEnums import CharState

class States(object):
    pass

class State(object):
    def __init__(self, world):
        self.world = world

    def onEnter(self):
        pass

    def act(self):
        pass

    def transition(self, state):
        States.currentState = state
        state.onEnter()


class Regen(State):
    def onEnter(self):
        self.world.log("-- Entering Regen state\n")
        self.world.send("rm")

    def act(self):
        self.world.log("-- Act in Regen state\n")
        vitals = self.world.gmcp['char']['vitals']
        if vitals['hp'] == vitals['maxhp'] and vitals['mana'] == vitals['maxmana'] and vitals['moves'] == vitals['maxmoves']:
            self.transition(States.lookingForFight)


class Fighting(State):
    def onEnter(self):
        self.world.log("-- Entering Fighting state\n")
        self.world.send('cast "acid arrow"')  # TODO: choose spell by current range and active cooldowns

    def act(self):
        # self.world.log("-- Act in Fighting state\n")
        if self.world.gmcp['char']['status']['state'] != CharState.fighting:
            self.transition(States.regen)


class LookingForFight(State):
    def onEnter(self):
        self.world.log("-- Entering LookingForFight state\n")
        self.world.send('look')  # TODO: triggers to trigger actual fighting

    def act(self):
        # self.world.log("-- Act in LookingForFight state\n")
        if self.world.gmcp['char']['status']['state'] == CharState.fighting:
            self.transition(States.fighting)


class Mage(BaseModule):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initStates()

    def initStates(self):
        States.lookingForFight = LookingForFight(self.mud.world)
        States.fighting = Fighting(self.mud.world)
        States.regen = Regen(self.mud.world)
        States.currentState = States.regen
        self.statemachine = States

    def handleGmcp(self, command, value):
        # States.currentState.act()
        pass

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
        self.log("-- Max mana")
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
