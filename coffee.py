import importlib
import traceback
import modular
importlib.reload(modular)


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
        'YOU ARE DYING OF THIRST!': 'drink barrel\nquit\ny',
        'YOU ARE DYING OF HUNGER!': 'eat bread\nquit\ny',
        }


class Coffee(modular.ModularClient):
    def __init__(self, mud, name):
        from modules.logging import Logging
        from modules.eval import Eval
        from modules.repeat import Repeat
        from modules.mapper import Mapper

        self.name = name
        self.logfname = '{}.log'.format(name)
        self.mapfname = '{}.map'.format(name)

        self.modules = {}
        mods = {
                'eval': (Eval, []),
                'repeat': (Repeat, []),
                'logging': (Logging, [self.logfname]),
                'mapper': (Mapper, [False, self.mapfname]),
                }
        if name == 'grumpy':
            from modules.gaoler import Gaoler
            mods['gaoler'] = (Gaoler, [])
        for modname, module in mods.items():
            try:
                constructor, args = module
                args = [mud] + args
                print("Constructing", constructor, "with", repr(args))
                self.modules[modname] = constructor(*args)
            except Exception:
                traceback.print_exc()

        super().__init__(mud)

        self.aliases.update(ALIASES)
        self.triggers.update(TRIGGERS)

        if name == 'cizra':
            self.triggers.update({
                    '(\w+): A closed door': lambda mud, matches: 'open ' + matches[0],
                    '(\w+) : A closed door': lambda mud, matches: 'open ' + matches[0],
                    'You point at .*, shooting forth a magic missile!': 'mm',
                    'You point at .*, shooting forth a blazing fireball!': 'ff',
                    'You are too close to .* to use Fireball.': 'mm',
                    'You point at .*, but nothing more happens.': 'ff',
                    'You point at .*, but fizzle the spell.': 'mm',
                    'You attempt to invoke magical protection, but fail.': 'cast mage armor',
                    'You shout combatively, but nothing more happens.': 'cast combat precognition',
                    })

    def getHostPort(self):
        return 'coffeemud.net', 2323


def getClass():
    return Coffee
