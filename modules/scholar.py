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

# TODO: book loaning

skills_by_level = {
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

def write(mud, matches=None):
    mud.send('stand')
    mud.send('write book "1111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111"')
    mud.send('sleep')

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
        if i in skills_by_level:
            for skill in skills_by_level[i]:
                out.append(skill)

    # don't wake when too low-level to actually do anything
    if out:
        mud.send("sta")
        for elem in out:
            mud.send(elem)
        mud.send("sleep")

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
                '#learnfrom (.+)': learnFrom,
                }

    def getTriggers(self):
        return {
            'Enter the name of the chapter:': '',
            'You are now in Add Text mode.': '\nq\ny',

            "(.+) whispers to you 'teach me (.+)'.": startLearning,
            ".+ fails to teach you (.+).": failedLearning, 
            'You are done learning (.+) from (.+).': doneLearning,
            'You already know (.+).': doneLearning,
            "You don't seem to know (.+).": tryAgainTeaching,
            ".+ has not learned the pre-requisites to (.+) yet.": doneTeaching,
            "You teach .+ '(.+)'": doneTeaching,
            "You attempt to write on .*, but mess up.": write,
            'You are hungry.': 'sta\neat bread\nsleep',
            'You are thirsty.': 'stand\nn\ndrink sink\ndrink sink\ndrink sink\ndrink sink\ns\nsleep',
            r'(Grumpy|Grumpier|Grumpiest) wants to teach you .*\.  Is this Ok .y.N..': 'y',
            }

    def getTimers(self):
        return {
                "practiceOne": (False, 5+2*600, 60, practiceOne),
                "practiceTwo": (False, 5+1*600, 615, practiceTwo),
                "write": (False, 605, 15, write),
                }

def getClass():
    return Scholar
