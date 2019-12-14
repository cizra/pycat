import importlib
import json
import traceback
import time

import modular


def trackTimeStart(mud, _):
    if 'honing' in mud.state:
        skill, counter = mud.state['honing']
        mud.send(skill)
        mud.state['honing'] = (skill, counter + 1)
        return

    mud.state['task_start_time'] = time.time()


def hone(mud, groups):
    skill = groups[0]
    mud.state['honing'] = (skill, 1)
    mud.send(skill)


def honed(mud, groups):
    skill = groups[0]
    if 'honing' in mud.state:
        mud.log("Honed {} in {} tries".format(skill, mud.state['honing'][1]))
        del mud.state['honing']
    mud.send("skill " + skill)

    if 'hones' not in mud.state:
        mud.state['hones'] = {}
    mud.state['hones'][skill] = time.time()
    mud.timers["hone_" + skill] = mud.mkdelay(301, lambda: mud.log("You can now hone " + skill))


def showHones(mud, _):
    found = False
    if 'hones' in mud.state:
        remove = set()
        now = time.time()
        for skill, honetime in mud.state['hones'].items():
            if now - honetime > 300:
                remove.add(skill)
            else:
                found = True
                mud.show("{}: {}s remaining".format(skill, 300 - int(now - honetime)))
        for skill in remove:
            del mud.state['hones'][skill]
        if not mud.state['hones']:
            del mud.state['hones']
    if not found:
        mud.show("No skills honed recently")


ALIASES = {
        'home': 'run 6s w 2s e 2n\nopen w\nw',
        'rt vassendar': 'run 4s d w d 2w d 2n 2e\nopen s\ns\nopen d\nrun 5d\nopen w\nw\nrun 8n w 2s 6w\nopen w\nrun 11w 3n 3w\nopen w\nrun 5w\nrun 3n 5w',
        'rt wgate': 'run 2s 3w\nopen w\nw',
        'rt sehaire': 'run w u 6w 2n 3w s 6w s 6w 2n 5w 5n w n w n 4w n e',
        '#hone (.+)': hone,
        '#hones': showHones,
        }

TRIGGERS = {
        'You feel a little cleaner, but are still very dirty.': 'bathe',
        'You feel a little cleaner.': 'bathe',
        'You feel a little cleaner; almost perfect.': 'bathe',
        'You are no longer hungry.': '!',
        'You are no longer thirsty.': '!',
        'You are starved, and near death.  EAT SOMETHING!': 'eat bread\nquit\ny',
        'You are dehydrated, and near death.  DRINK SOMETHING!': 'drink sink\nquit\ny',
        'YOU ARE DYING OF THIRST!': 'drink barrel\nquit\ny',
        'YOU ARE DYING OF HUNGER!': 'eat bread\nquit\ny',
        'You start .*\.': trackTimeStart,
        'You study .*\.': trackTimeStart,
        'You are done (.*)\.': lambda mud, matches: mud.mud.log("The task took {}s".format(time.time() - mud.state['task_start_time'])),
        'You become better at (.+).': honed,
        }
with open('passwords.json', 'rb') as pws:
    TRIGGERS.update(json.load(pws))


class Coffee(modular.ModularClient):
    def __init__(self, mud, name):

        self.name = name
        self.logfname = '{}.log'.format(name)
        self.mapfname = 'coffee.map'

        import modules.logging
        import modules.eval
        import modules.mapper
        importlib.reload(modular)
        importlib.reload(modules.logging)
        importlib.reload(modules.eval)
        importlib.reload(modules.mapper)

        self.modules = {}
        mods = {
                'eval': (modules.eval.Eval, []),
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
        self.triggers.update({r'\(Enter your character name to login\)': name})

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

                    # spell failures
                    'You point at .*, but nothing more happens.': 'ff',
                    'You point at .*, but fizzle the spell.': 'mm',
                    'You attempt to invoke magical protection, but fail.': 'cast mage armor',
                    'You shout combatively, but nothing more happens.': 'cast combat precognition',
                    'You cast a spell on yourself, but the magic fizzles.': 'cast fly',
                    'You attempt to invoke a spell, but fail miserably.': 'cast shield',

                    # recasts
                    'Your magical armor fades away.': 'cast mage armor',
                    'You begin to feel a bit more vulnerable.': 'cast shield',
                    'The light above you dims.': 'cast light',
                    'Your combat precognition fades away.': 'cast combat prec',
                    'You begin to float back down.': 'cast fly',
                    'Your skin softens.': 'cast stoneskin',
                    })
        if name == 'rhubard' or name == 'bombard':
            self.triggers.update({
                'Drab appears!': 'fol drab',
                'Drab recalls body and spirit to the Java Plane!': 'recall',
                'Drab lays down and takes a nap.': 'sleep',
                'Drab mounts a gelding.': 'mount 2.gelding',
                'Drab dismounts a gelding.': 'dismo',
                'Drab takes a drink from a fountain.': 'drink fount',
                })

    def getHostPort(self):
        return 'coffeemud.net', 2323

    def level(self):
        return self.gmcp['char']['status']['level']

    def exprate(self):
        if 'char' not in self.gmcp or 'status' not in self.gmcp['char'] or 'tnl' not in self.gmcp['char']['status']:
            return

        if 'exprate_prev' not in self.state:
            self.state['exprate_prev'] = self.gmcp['char']['status']['tnl']
        else:
            now = self.gmcp['char']['status']['tnl']
            self.log("Exp per hour: {}".format(self.state['exprate_prev'] - now))
            self.state['exprate_prev'] = now


    def getTimers(self):
        return {
                "exprate": (False, 60*60, 30, self.exprate),
                }

    def handleGmcp(self, cmd, value):
        super().handleGmcp(cmd, value)
        if cmd == 'char.status' and 'pos' in value and 'fatigue' in value and 'maxstats' in self.gmcp['char']:
            if value['pos'] == 'Sleeping' and value['fatigue'] == 0 and self.gmcp['char']['vitals']['moves'] == self.gmcp['char']['maxstats']['maxmoves']:
                self.log("Rested!")

        if cmd == 'char.vitals' and 'maxstats' in self.gmcp['char']:
            if self.gmcp['char']['status']['pos'] == 'Sleeping' and self.gmcp['char']['vitals']['hp'] == self.gmcp['char']['maxstats']['maxhp']:
                # self.log("Healed!")
                pass

        if cmd == 'char.vitals' and 'maxstats' in self.gmcp['char']:
            if self.gmcp['char']['status']['pos'] == 'Sleeping' and self.gmcp['char']['vitals']['mana'] > 100:
                # self.log("Full mana!")
                if self.name == 'hippie':
                    self.send("sta\nchant speed time\ndrink sink\nsleep")


def getClass():
    return Coffee
