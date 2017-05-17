import importlib
import coffee
importlib.reload(coffee)
import collections
import re
import subprocess



ALIASES = {
        }
TRIGGERS = {
        # retries
        'You study .*, looking more frustrated every second.': '!',
        'You attempt to invoke magical protection, but fail.': 'cast mage armor',
        'You attempt to invoke light, but fail.': 'cast light',

        # sustains
        'Your magical armor fades away.': 'cast mage armor',
        'You begin to feel a bit more vulnerable.': 'cast shield',
        'The light above you dims.': 'cast light',
        'Your skin softens.': 'cast stoneskin',

        # combat flow
        'You attempt to invoke a spell, but fail miserably.': '!',
        'You point at .*, shooting forth a blazing fireball!': 'ff',
        'You point at .*, but nothing more happens.': 'ff',
        'You are too close to .* to use Fireball\.': 'mm',
        'You point at .*, shooting forth a magic missile!': 'mm',
        'You point at .*, but fizzle the spell.': 'mm',

        # vassendar
        'A hissing lizard crawls in from the .*.': 'mm lizard',
        # sengalion
        'The field trainer appears!': 'ff trainer',
        'The field trainer arrives from the .*\.': 'ff trainer',
        # 'A new initiate arrives from the .*\.': 'ff fresh',
        # 'A freshly inducted inititate practices their first forms\.': 'ff fresh',
        'A trainer paces the courtyard correcting the initiates.': 'ff trainer',
        }
NOTIFICATIONS = {
        }


class Mage(coffee.Coffee):
    def __init__(self, mud):
        super().__init__(mud)
        self.aliases.update(ALIASES)
        self.triggers.update(TRIGGERS)
        self.notifications.update(NOTIFICATIONS)


def get_class():
    return Mage
