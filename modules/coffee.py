from modules.basemodule import BaseModule

import re


ALIASES = {
        'home': 'run 6s w 2s e 2n\nopen w\nw',
        'rt vassendar': 'run 4s d w d 2w d 2n 2e\nopen s\ns\nopen d\nrun 5d\nopen w\nw\nrun 8n w 2s 6w\nopen w\nrun 11w 3n 3w\nopen w\nrun 5w\nrun 3n 5w',
        'rt wgate': 'run 2s 3w\nopen w\nw',
        'rt sehaire': 'run w u 6w 2n 3w s 6w s 6w 2n 5w 5n w n w n 4w n e',
        }
TRIGGERS = {
        'You feel a little cleaner, but are still very dirty.': 'bathe',
        'You feel a little cleaner.': 'bathe',
        'You feel a little cleaner; almost perfect.': 'bathe',
        'You are no longer hungry.': '!',
        'You are no longer thirsty.': '!',
        'You are starved, and near death.  EAT SOMETHING!': 'quit\ny',
        'You are dehydrated, and near death.  DRINK SOMETHING!': 'quit\ny',
        'YOU ARE DYING OF THIRST!': 'quit\ny',
        'YOU ARE DYING OF HUNGER!': 'quit\ny',
        }


class Coffee(BaseModule):
    def __init__(self, mud):
        super().__init__(mud)
        self.aliases.update(ALIASES)
        self.triggers.update(TRIGGERS)

    def getHostPort(self):
        # return '::1', 4000
        return 'coffeemud.net', 2323
