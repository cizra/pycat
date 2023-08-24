from modules.basemodule import BaseModule

import random
import re
import time


# start with at least 10 charisma, max int and wis
# At level 1, train scholar, practice write, prac floristry
# At level 2, write book
# At level 3, gain engraving and embroidering, prac herbology
# At level 4, gain combat log
# At level 5, organizing
# At level 7, gain find home
# At level 10, gain wilderness lore
# At level 11, gain book naming
# At level 13, gain find ship
# At level 14, gain make maps
# At level 16, gain plant lore
# At level 22, gain planar lore
# At level 30, gain master herbology and master floristry

# TODO: book loaning

skills_by_level = {
        1: ['herb herb', 'florist flower'],
        2: ['label book', 'engrave bowl bowl', 'embroider sock sock'],
        3: ['light fire', 'combatlog self', 'combatlog stop', 'organ room name'],#'smokesig testing testing 1 2 3'],
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
        29: ['mherb herb', 'mflo flo'],
        }

def write(mud, lag=1):
    if mud.gmcp['room']['info']['num'] != 1741703288:
        mud.log("Not running Scholar script - must be in Pecking Place")
        return

    def end(finalStr):
        mud.log("Removing write triggers")
        mud.send(finalStr)
        lagSend(mud, 1, 'sleep')
        # del mud.triggers['You are now in Add Text mode.']
        # del mud.triggers['Menu ...A.D.L.I.E.R.S.Q.W.:']
        # del mud.triggers['Quit without saving .N.y..']

    def sleep(mud, matches):
        if mud.gmcp['room']['info']['num'] != 1741703288:
            mud.log("Not running Scholar script - must be in Pecking Place")
        mud.send("\nsleep")

    mud.log("Adding write triggers")
    mud.triggers['You are now in Add Text mode.'] = '\n'
    mud.triggers['Menu ...A.D.L.I.E.R.S.Q.W.:'] = 'q'
    mud.triggers['Quit without saving .N.y..'] = lambda mud, groups: end('y')
    mud.triggers['Enter the name of the chapter:'] = sleep
    mud.triggers['Enter an empty line to exit.'] = '\nblarg'

    lagSend(mud, lag, 'stand')
    lagSend(mud, lag + 1, 'write book "1111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111"')

def practiceOne(mud):
    level = mud.level() - 1
    mud.log("practiceOne")
    practiceImpl(mud, level, 0, -2)

def practiceTwo(mud):
    mud.log("practiceTwo")
    level = mud.level() - 1
    practiceImpl(mud, level-1, 0, -2)

def lagSend(mud, lag, cmd):
    mud.log("Enqueueing " + cmd + " @ " + str(lag))
    def logAndSend(cmd):
        mud.log("laggy send " + cmd)
        mud.send(cmd)
    mud.timers["lagsend_" + cmd] = mud.mkdelay(lag, lambda m, cmd=cmd: logAndSend(cmd))

def practiceImpl(mud, begin, end, step):
    if mud.gmcp['room']['info']['num'] != 1741703288:
        mud.log("Not running Scholar script - must be in Pecking Place")
        return

    out = []
    lag = 1
    mud.send("stand")

    for i in range(begin, end, step):
        if i in skills_by_level:
            for skill in skills_by_level[i]:
                lagSend(mud, lag, skill)
                lag += 1
    write(mud, lag)
    return

def learnFrom(mud, matches):
    if 'learn' not in mud.state:
        mud.state['learn'] = {}
    mud.state['learn']['from'] = matches[0]

def startLearning(mud, matches):
    if 'learn' not in mud.state:
        mud.state['learn'] = {}
    mud.state['learn']['learner'] = matches[0]
    if 'from' not in mud.state['learn']:
        mud.state['learn']['from'] = 'guildmaster'
    mud.send("study {} {}".format(mud.state['learn']['from'], matches[1]))


def failedLearning(world, matches):
    if 'learn' not in world.state:
        return
    world.state['learn']['failed'] = True
    world.send("study {} {}".format(world.state['learn']['from'], matches[0]))

def doneLearning(world, matches):
    if 'learn' not in world.state:
        return
    state = world.state['learn']

    if 'failed' not in state:
        world.send("teach " + state['learner'] + " " + matches[0])
    else:
        del state['failed']

def tryAgainTeaching(world, matches):
    if 'learn' not in world.state:
        return
    if 'times' not in world.state['learn']:
        world.state['learn']['times'] = 0
    world.state['learn']['times'] += 1
    if world.state['learn']['times'] < 10:
        world.send("teach " + world.state['learn']['learner'] + " " + matches[0])

def doneTeaching(world, matches):
    world.send('study forget ' + matches[0])
    del world.state['learn']

class Scholar(BaseModule):
    def getAliases(self):
        return {
                self.mud.cmd_char + 'learnfrom (.+)': learnFrom,
                }

    def getTriggers(self):
        return {
            '^You regain your feet.': 'sleep',
            '^You have 58 points remaining.': 'wis 15\nint 15\ncha 7\ncon 15\nstr 6\n\n',
            '^You have 64 points remaining.': 'wis 15\nint 15\ncha 7\ncon 15\nstr 12\n\n',
            '^Please choose from the following Classes:': 'apprentice',
            '^Is Apprentice correct': 'y',
            '^You have remorted back to level 1!': 'run n w\ntrain scholar\ntrain int\ntrain int\ntrain int\ntrain int\nprac write\nrun e s\nsay help',
            # 'You are now in Add Text mode.': lambda mud, groups: [mud.log("Add text handler"), mud.send('q'), mud.send('y')],
            "(.+) whispers to you 'teach me (.+)'.": startLearning,
            ".+ fails to teach you (.+).": failedLearning,
            'You are done learning (.+) from (.+).': doneLearning,
            'You already know (.+).': doneLearning,
            "You don't seem to know (.+).": tryAgainTeaching,
            ".+ has not learned the pre-requisites to (.+) yet.": doneTeaching,
            "You teach .+ '(.+)'": doneTeaching,
            "You attempt to write on .*, but mess up.": lambda mud, groups: write(mud, 1),
            "You don't have enough movement to do that.  You are too tired.": 'sleep',
            "You don't have enough mana to do that.": 'sleep',
            'You are hungry.': 'sta\neat bread\nsleep',
            'You are thirsty.': 'stand\ndrink sink\ndrink sink\ndrink sink\ndrink sink\nsleep',
            }

    def getOneTimeTriggers(self):
        if self.world.name == 'grumpy':
            return {}
        else:
            return {
                    '^\(You are asleep\)$': 'stand',
                    '^Grumpy appears!$': 'fol grumpy\nsleep',
                    }

    def getTimers(self):
        return {
                "practiceOne": (False, 5+600, 60, practiceOne),
                "practiceTwo": (False, 5+600, 615, practiceTwo),
                }

def getClass():
    return Scholar
