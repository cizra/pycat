import importlib
import modular

import modules.logging
import modules.eval
import modules.coffee
import modules.repeat
importlib.reload(modular)
importlib.reload(modules.logging)
importlib.reload(modules.eval)
importlib.reload(modules.repeat)
importlib.reload(modules.coffee)
MODULES = [
        modules.eval.Eval,
        modules.repeat.Repeat,
        modules.coffee.Coffee,
        ]


class Client(modular.ModularClient):
    def __init__(self, mud):
        super().__init__(mud)
        self.modules = [m(mud) for m in MODULES] + [modules.logging.Logging(mud, 'new.log')]


def getClass():
    return Client
