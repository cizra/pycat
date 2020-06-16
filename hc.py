import importlib
import json
import traceback
import time

import coffee
importlib.reload(coffee)
import modular
importlib.reload(modular)


class Hc(coffee.Coffee):
    def __init__(self, mud, name):
        super().__init__(mud, name)
        with open('passwords_hc.json', 'rb') as pws:
            self.triggers.update(json.load(pws))

    def getHostPort(self):
        return 'coffeemud.net', 2325


def getClass():
    return Hc
