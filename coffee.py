import importlib
import json
import traceback
import time

import modular

from modules.coffee_hones import honeToType

def noHone(mud, _):
    if 'honing' in mud.state:
        skill, counter = mud.state['honing']
        mud.send(skill)
        mud.state['honing'] = (skill, counter + 1)

def trackTimeStart(mud, _):
    if 'honing' in mud.state:
        noHone(mud, None)
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

    if skill in honeToType:
        honeType = honeToType[skill]
    else:
        honeType = 'skill'

    mud.timers["honed_skill_scrape_" + skill] = mud.mkdelay(1, lambda m: mud.send(honeType + ' ' + skill))

    if 'hones' not in mud.state:
        mud.state['hones'] = {}
    mud.state['hones'][skill] = time.time()

    if 'hone_on_success' in mud.state:
        mud.state['hone_on_success'](skill)

    if skill in mud.state['skillLevels'] and mud.state['skillLevels'][skill] > 99:
        return
    mud.timers["hone_again_notification_for_" + skill] = mud.mkdelay(301, lambda m: mud.log("You can now hone " + skill))


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
                mud.show("{}: {}s remaining\n".format(skill, 300 - int(now - honetime)))
        for skill in remove:
            del mud.state['hones'][skill]
        if not mud.state['hones']:
            del mud.state['hones']
    if not found:
        mud.show("No skills honed recently")


def setSkillLevel(mud, groups):
    if 'skillLevels' not in mud.state:
        mud.state['skillLevels'] = {}

    level = int(groups[0])
    skill = groups[1]

    mud.state['skillLevels'][skill] = level

ALIASES = {
        'newcharsetup': """prompt %T ^N^h%h/%Hh^q ^m%m/%Mm^q ^v%v/%Vv^q %aa %-LEVELL %Xtnl %z^N %E %B\ny
        colorset\nclantalk\npurple\nwhite\n\ncolorset\n14\ngrey\n
        colorset\n16\nblue\nwhite\n
        config copy grumpy\ny
        alias define on open n~n
        alias define oe open e~e
        alias define ow open w~w
        alias define os open s~s
        alias define od open d~d
        alias define ou open u~u
        alias define un unlock n~open n~n
        alias define ue unlock e~open e~e
        alias define us unlock s~open s~s
        alias define uw unlock w~open w~w
        alias define uu unlock u~open u~u
        alias define ud unlock d~open d~d
        """,
        'home': lambda mud, _: mud.modules['mapper'].go('1115504774', 'go'),
        '#hone (.+)': hone,
        '#hones': showHones,
        }

TRIGGERS = {
        'You slip on the cold wet ground.': 'stand',
        'You fall asleep from exhaustion!!': 'stand\nsleep',
        r'(Grumpy|Grumpier|Grumpiest|Madcrank) wants to teach you .*\.  Is this Ok .y.N..': 'y',
        '.* is DEAD!!!': 'look in body',
        'You parry ': 'disarm',
        'You attempt to disarm .* and fail!': 'disarm',
	'A floating log gets caught on the bank.  It is large enough to enter and ride': 'enter log\ne',
	'A turtle shell gets caught on the rock.  It is large enough to enter.': 'enter shell\nn',
        # "A set of wooden footholds lead up to the top of the coach": 'u\nsay high road',
        'Midgaard, a most excellent small city to start in.': 'say Midgaard',
        "Mrs. Pippet says to you 'If ye're still wanting to go to Midgaard then say": 'say Ready to go!',
        'Grumpy wants you to try to teach him about .*\. It will': 'y',
        'You feel a little cleaner, but are still very dirty.': 'bathe',
        'You feel a little cleaner.': 'bathe',
        'You feel a little cleaner; almost perfect.': 'bathe',
        'You are no longer hungry.': '!',
        'You are no longer thirsty.': '!',
        'You are starved, and near death.  EAT SOMETHING!': 'sta\neat bread\nquit\ny',
        'You are dehydrated, and near death.  DRINK SOMETHING!': 'sta\ndrink sink\nquit\ny',
        'YOU ARE DYING OF THIRST!': 'sta\ndrink barrel\nquit\ny',
        'YOU ARE DYING OF HUNGER!': 'sta\neat bread\nquit\ny',
        'Quit -- are you sure .y.N..': 'y',
        'You start .*\.': trackTimeStart,
        'You study .*\.': trackTimeStart,
        # "Grumpy already knows 'Organizing'.": noHone,
        'You are done (.*)\.': lambda mud, matches: mud.mud.log("The task took {}s".format(time.time() - (mud.state['task_start_time'] if 'task_start_time' in mud.state else 0))),
        'You become better at (.+).': honed,
        '.* subtly sets something on the ground.': 'get bag\nput bag box\nexam box',
        "The mayor says, 'I'll give you 1 minute.  Go ahead....ask for your reward.'": 'say reward',
        "The mayor says 'Hello .*. Hope you are enjoying your stay.'": 'drop box\nsay These obligations have been met.',
        '^\[(\d  |\d\d |\d\d\d)%\] ([^[]+)$': setSkillLevel,
        }
with open('passwords.json', 'rb') as pws:
    TRIGGERS.update(json.load(pws))


class Coffee(modular.ModularClient):
    def __init__(self, mud, name):

        self.name = name
        self.logfname = '{}.log'.format(name)
        self.commfname = '{}.comm'.format(name)
        self.mapfname = 'coffee.map'

        import modules.logging
        import modules.eval
        import modules.mapper
        import modules.commlog
        importlib.reload(modular)
        importlib.reload(modules.logging)
        importlib.reload(modules.eval)
        importlib.reload(modules.mapper)
        importlib.reload(modules.commlog)

        self.modules = {}
        mods = {
                'eval': (modules.eval.Eval, []),
                'logging': (modules.logging.Logging, [self.logfname]),
                'commlog': (modules.commlog.CommLog, [self.commfname]),
                'mapper': (modules.mapper.Mapper, [False, self.mapfname]),
                }
        if name == 'grovel':
            import modules.spellups
            importlib.reload(modules.spellups)
            mods['spellups'] = (modules.spellups.Spellups, [])
        if name in set(['awugray', 'madcrank', 'grumpy', 'grumpiest', 'amoli', 'cizra']):
            import modules.scholar
            importlib.reload(modules.scholar)
            mods['scholar'] = (modules.scholar.Scholar, [])
        elif name in set(['vassal', 'robot', 'busybee']):
            import modules.autosmith
            importlib.reload(modules.autosmith)
            mods['autosmith'] = (modules.autosmith.AutoSmith, [])
        elif name == 'landscapegoat':
            import modules.gatherer
            importlib.reload(modules.gatherer)
            mods['gatherer'] = (modules.gatherer.Gatherer, [])
        elif name == 'aslei':
            import modules.mage
            importlib.reload(modules.mage)
            mods['mage'] = (modules.mage.Mage, [])

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
        self.aliases.update({
            '#autohone ([^,]+), (.+)': lambda mud, groups: self.startAutoHone(groups[0], groups[1]),
                })
        self.triggers.update(TRIGGERS)
        self.oneTimeTriggers.update({r'\(Enter your character name to login\)': name})

        if name == 'zerleha':
            self.triggers.update({
                'You are now listed as AFK.': 'sc',
                'You are hungry.': 'eat bread',
                'You are thirsty.': 'drink drum',
                })
        elif name == 'grumpier':  # monk
            self.aliases.update({
                'kk( +.+)?': lambda mud, groups: self.stackToLag('gouge\ntrip\ndirt\nax\nkick\nbodyflip\natemi\nbodytoss\nemote is done with stacking `kk`.', groups[0]),
                })
            # self.triggers.update({
             #    'You is done with stacking `(.+)`.': lambda mud, groups: self.stackToLag('gouge\ntrip\nax\nkick\nbodyflip\nbodytoss\nemote is done with stacking `kk`.', groups[0]),
              #   })
        elif name == 'punchee':  # group leader
            self.aliases.update({
                'waa': 'sta\nwake cizra\nwake basso',
                })
        elif name == 'basso' or name == 'cizra':  # followers
            self.triggers.update({
                    'Punchee lays down and takes a nap.': 'sleep',
                    })
        elif name == 'cizra':
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

    def stackToLag(self, cmds, target):
        lag = 0
        cmd = cmds.split('\n')[0]
        if target:
            cmd = cmd + target
        self.send(cmd)
        for cmd in cmds.split('\n')[1:]:
            self.timers["stackToLag" + cmd] = self.mkdelay(lag, lambda m, cmd=cmd: self.mud.send(cmd))
            lag += 2.6

    def getHostPort(self):
        return 'coffeemud.net', 2324

    def level(self):
        return self.gmcp['char']['status']['level']

    def exprate(self, mud):
        if 'char' not in self.gmcp or 'status' not in self.gmcp['char'] or 'tnl' not in self.gmcp['char']['status']:
            return

        if 'exprate_prev' not in self.state:
            self.state['exprate_prev'] = self.gmcp['char']['base']['perlevel'] - self.gmcp['char']['status']['tnl']
        else:
            now = self.gmcp['char']['base']['perlevel'] - self.gmcp['char']['status']['tnl']
            self.log("Exp per hour: {}".format(now - self.state['exprate_prev']))
            self.state['exprate_prev'] = now


    def getTimers(self):
        return {
                "exprate": (False, 60*60, 30, self.exprate),
                }

    def onMaxMana(self):
        if 'mage' in self.modules:
            self.modules['mage'].onMaxMana()

    def handleGmcp(self, cmd, value):
        super().handleGmcp(cmd, value)
        if cmd == 'char.status' and 'pos' in value and 'fatigue' in value and 'maxstats' in self.gmcp['char']:
            if value['pos'] == 'Sleeping' and value['fatigue'] == 0 and self.gmcp['char']['vitals']['moves'] == self.gmcp['char']['maxstats']['maxmoves']:
                self.log("Rested!")
        if cmd == 'char.vitals' and 'status' in self.gmcp['char'] and 'maxstats' in self.gmcp['char']:
            if self.gmcp['char']['status']['pos'] == 'Sleeping' and value['mana'] == self.gmcp['char']['maxstats']['maxmana']:
                self.onMaxMana()

        if cmd == 'char.vitals' and 'maxstats' in self.gmcp['char']:
            if 'prevhp' in self.state and self.gmcp['char']['status']['pos'] == 'Sleeping':
                hp = self.gmcp['char']['vitals']['hp']
                maxhp = self.gmcp['char']['maxstats']['maxhp']
                if hp == maxhp and self.state['prevhp'] < maxhp:
                    self.log("Healed!")
                self.state['prevhp'] = hp
                pass

        if cmd == 'char.vitals' and 'maxstats' in self.gmcp['char']:
            if self.gmcp['char']['status']['pos'] == 'Sleeping' and self.gmcp['char']['vitals']['mana'] > 100:
                # self.log("Full mana!")
                if self.name == 'hippie':
                    self.send("sta\nchant speed time\ndrink sink\nsleep")

    def startAutoHone(self, skill, cmd):
        self.log("Autohoning {} as {}".format(skill, cmd))
        self.timers['autohone_' + cmd] = self.mktimernow(60*5 + 1, lambda mud: self.honeTimer(skill, cmd))

    def honeTimer(self, skill, cmd):
        def onHoneSuccess(skillHoned):
            if skill == skillHoned:
                if skill in self.state['skillLevels'] and self.state['skillLevels'][skill] >= 99:
                    self.log("Removing " + skill + " from autohone")
                    del self.timers['autohone_' + cmd]
                else:
                    self.setTimerRemaining('autohone_' + cmd, 301)
                    self.send('sleep')

        # multi-hone timers need work
        self.state['hone_on_success'] = onHoneSuccess
        self.state['honing'] = (cmd, 1)
        self.send('sta\n{}'.format(cmd))


def getClass():
    return Coffee
