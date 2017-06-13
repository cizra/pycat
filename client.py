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
MODULES = {  # determines the pecking order
        'eval': modules.eval.Eval,
        'repeat': modules.repeat.Repeat,
        'gaoler': modules.gaoler.Gaoler,
        'coffee': modules.coffee.Coffee,
        }


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

        self.modules = {}
        for name, module in MODULES.items():
            try:
                self.modules[name] = module(mud)
            except Exception:
                traceback.print_exc()
        try:
            self.modules['logging'] = modules.logging.Logging(mud, self.logfname)
        except Exception:
            traceback.print_exc()

        try:
            self.modules['mapper'] = modules.mapper.Mapper(mud, self.mapfname)
        except Exception:
            traceback.print_exc()

        super().__init__(mud)


def getClass():
    return Client
