import importlib
import traceback
import modular

import modules.logging
import modules.eval
import modules.repeat
import modules.coffee
import modules.mapper
import modules.gaoler
importlib.reload(modular)
importlib.reload(modules.logging)
importlib.reload(modules.eval)
importlib.reload(modules.repeat)
importlib.reload(modules.coffee)
importlib.reload(modules.gaoler)
importlib.reload(modules.mapper)
MODULES = [  # determines the pecking order
        modules.eval.Eval,
        modules.repeat.Repeat,
        modules.coffee.Coffee,
        modules.gaoler.Gaoler,
        ]


class Client(modular.ModularClient):
    def __init__(self, mud):
        try:
            self.logfname
        except AttributeError:
            self.logfname = 'new.log'

        try:
            self.mapfname
        except AttributeError:
            self.mapfname = 'default.map'

        self.modules = []
        for m in MODULES:
            try:
                self.modules.append(m(mud))
            except Exception:
                traceback.print_exc()
        try:
            self.modules.append(modules.logging.Logging(mud, self.logfname))
        except Exception:
            traceback.print_exc()

        # TODO: sucks. Switch to dicts, iterate over values in parent
        try:
            self.mapper = modules.mapper.Mapper(mud, self.mapfname)
        except Exception:
            traceback.print_exc()
        self.modules.append(self.mapper)

        super().__init__(mud)


def getClass():
    return Client
