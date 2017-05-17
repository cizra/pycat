import importlib
import coffee
importlib.reload(coffee)
import collections
import re
import subprocess



ALIASES = {
        }
TRIGGERS = {
        'Grumpy starts ': 'play tempo',
        'Grumpy vanishes in a puff of smoke.': 'quit;y',
        'You hit a foul note.': '!',
        }
NOTIFICATIONS = {
        }


class Bard(coffee.Coffee):
    def __init__(self, mud):
        super().__init__(mud)
        self.aliases.update(ALIASES)
        self.triggers.update(TRIGGERS)
        self.notifications.update(NOTIFICATIONS)


def get_class():
    return Bard
