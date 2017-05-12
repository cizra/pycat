import importlib
import base
importlib.reload(base)
import collections
import re
import subprocess
import time


ALIASES = {
        'home': 'run 6s w 2s e 2n w',
        }
TRIGGERS = {
        'You feel a little cleaner, but are still very dirty.': 'bathe',
        'You feel a little cleaner.': 'bathe',
        'You feel a little cleaner; almost perfect.': 'bathe',
        'You are no longer hungry.': '!',
        'You are no longer thirsty.': '!',
        }
NOTIFICATIONS = {
        }


class Coffee(base.BaseClient):
    def __init__(self, mud):
        super().__init__(mud)
        self.aliases.update(ALIASES)
        self.triggers.update(TRIGGERS)
        self.notifications.update(NOTIFICATIONS)

    def get_host_port():
        return 'coffeemud.net', 23

    def trigger2(self, line):
        if re.match('^You start .+', line):
            self.state['job_start'] = time.time()
        elif re.match('^You are done .+', line) and 'job_start' in self.state:
            self.log('Job took {} seconds'.format(time.time() - self.state['job_start']))



def get_class():
    return Coffee
