from modules.basemodule import BaseModule

import random
import re
import time


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


class Scholar(BaseModule):
    def getTriggers(self):
        return {
            'You are thirsty.': 'drink barrel',
            'You are hungry.': 'eat bread',
            'Enter the name of the chapter:': '',
            }

    def practice(self):
        self.send("sta")
        self.send("organ room name")
        self.send("findhome")
        self.send("speculate")
        self.send("light fire")
        self.send("recollect happy") # 18
        self.send("plore astral") # 21
        self.send("survey room book")
        self.send("wlore")
        self.send("rlore human")
        self.send("lore book")
        self.send("combatlog self")
        self.send("combatlog stop")
        self.send("knowplant book")
        self.send("bname book 1 book")
        self.send("bookedit book")
        self.send("entitle book book")
        self.send("label book")
        self.send("cwrite book")
        self.send("findship")
        self.send("map paper")
        self.send("engrave drum drum")
        self.send("embroider belt belt")
        self.send("wlp")  # alias, write long string to book
        self.send("sleep")

    def getTimers(self):
        return {
                "practice": (False, 605, 5, self.practice),
                }

def getClass():
    return Scholar
