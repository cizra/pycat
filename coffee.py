import importlib
import traceback
import modular



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
        'You are starved, and near death.  EAT SOMETHING!': 'eat bread\nquit\ny',
        'You are dehydrated, and near death.  DRINK SOMETHING!': 'drink barrel\nquit\ny',
        'YOU ARE DYING OF THIRST!': 'drink barrel\nquit\ny',
        'YOU ARE DYING OF HUNGER!': 'eat bread\nquit\ny',
        }


class Coffee(modular.ModularClient):
    def __init__(self, mud, name):

        self.name = name
        self.logfname = '{}.log'.format(name)
        self.mapfname = '{}.map'.format(name)

        import modules.logging
        import modules.eval
        import modules.repeat
        import modules.mapper
        importlib.reload(modular)
        importlib.reload(modules.logging)
        importlib.reload(modules.eval)
        importlib.reload(modules.repeat)
        importlib.reload(modules.mapper)

        self.modules = {}
        mods = {
                'eval': (modules.eval.Eval, []),
                'repeat': (modules.repeat.Repeat, []),
                'logging': (modules.logging.Logging, [self.logfname]),
                'mapper': (modules.mapper.Mapper, [False, self.mapfname]),
                }
        if name == 'grumpy':
            import modules.gaoler
            importlib.reload(modules.gaoler)
            mods['gaoler'] = (modules.gaoler.Gaoler, [])
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

        if name == 'zerleha':
            self.triggers.update({
                'You are now listed as AFK.': 'sc',
                'You are hungry.': 'eat bread',
                'You are thirsty.': 'drink drum',
                })
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
