from modules.basemodule import BaseModule

import random
import re
import time


# At level 1, train scholar
# At level 2, kill a monster in mud school
# At level 3, practice write, gain herbology, engraving and embroidering
# At level 4, gain combat log
# At level 5, gain organizing
# At level 7, gain find home
# At level 11, gain book naming
# At level 13, gain find ship
# At level 14, gain make maps
# At level 16, gain plant lore
# At level 22, gain planar lore
# At level 30, gain master herbology

# TODO: book loaning

skills_by_level = {
        1: ['herb herb', 'wlp'],
        2: ['label book', 'engrave drum drum', 'embroider belt belt'],
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
    practiceImpl(mud, level, 10, -1)

def practiceTwo(mud):
    mud.log("practiceTwo")
    practiceImpl(mud, 10, 0, -1)

def practiceImpl(mud, begin, end, step):
    # TODO: only work in the right room
    mud.send("sta")

    for i in range(begin, end, step):
        if i in skills_by_level:
            for skill in skills_by_level[i]:
                mud.send(skill)

    mud.send("sleep")
    return


def startLearning(world, matches):
    world.state['learn'] = {'learner': matches[0]}
    world.send("study brock " + matches[1])


def failedLearning(world, matches):
    if 'learn' not in world.state:
        return
    world.state['learn']['failed'] = True
    world.send("study brock " + matches[0])

def doneLearning(world, matches):
    if 'learn' not in world.state:
        return
    state = world.state['learn']

    if 'failed' not in state:
        world.send("teach " + state['learner'] + " " + matches[0])
    else:
        del state['failed']

def doneTeaching(world, matches):
    world.send('study forget ' + matches[0])
    del world.state['learn']

class Scholar(BaseModule):

    def getTriggers(self):
        return {
            'You are thirsty.': 'drink barrel',
            'You are hungry.': 'eat bread',
            'Enter the name of the chapter:': '',
            'You are now in Add Text mode.': '\nq\ny',

            "(.+) whispers to you 'teach me (.+)'.": startLearning,
            "Guildmaster Brock fails to teach you (.+).": failedLearning, 
            'You are done learning (.+) from Guildmaster Brock.': doneLearning,
            "You teach .+ '(.+)'": doneTeaching,
            }

    def getTimers(self):
        return {
                "practiceOne": (False, 605, 15, practiceOne),
                "practiceTwo": (False, 605, 315, practiceTwo),
                }

def getClass():
    return Scholar
