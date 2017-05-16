import importlib
import coffee
importlib.reload(coffee)
import collections
import re
import subprocess



ALIASES = {
        }
TRIGGERS = {
        'Extreme emotions disrupt your chant.': '!',
        'You chant to commune with nature, but lose concentration.': '!',
        'You chant to .*, but the magic fades\.': '!',  # sunray
        '.* goes blind!': 'cha venom',
        'You chant at .*, but nothing happens\.': '!',  # venomous bite
        }
NOTIFICATIONS = {
        }


class Druid(coffee.Coffee):
    def __init__(self, mud):
        super().__init__(mud)
        self.aliases.update(ALIASES)
        self.triggers.update(TRIGGERS)
        self.notifications.update(NOTIFICATIONS)


def get_class():
    return Druid
