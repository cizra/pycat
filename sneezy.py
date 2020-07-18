import importlib
import json
import time
import traceback

import modular
import modules.gzlogging
import modules.eval
# import modules.repeat
import modules.mapper
importlib.reload(modular)
importlib.reload(modules.gzlogging)
importlib.reload(modules.eval)
# importlib.reload(modules.repeat)
importlib.reload(modules.mapper)

honeToType = {
        'heal light': 'cleric',
        'harm light': 'cleric',
        'armor': 'cleric',
        'bless': 'cleric',
        'rain brimstone': 'cleric',
        'clot': 'cleric',
        'create food': 'cleric',
        'create water': 'cleric',
        'cure poison': 'cleric',
        'salve': 'cleric',
        'heal serious': 'cleric',
        'sterilize': 'cleric',
        'remove curse': 'cleric',
        'cure disease': 'cleric',
        'refresh': 'cleric',
        'heal critical': 'cleric',
        'harm serious': 'cleric',
        'cure blindness': 'cleric',
        'cleric repair': 'cleric',
        'expel': 'cleric',
        'flamestrike': 'cleric',
        'curse': 'cleric',
        'disease': 'cleric',
        'harm critical': 'cleric',
        'numb': 'cleric',
        'poison': 'cleric',
        'infect': 'cleric',
        'heal': 'cleric',
        'summon': 'cleric',
        'harm': 'cleric',
        'plague of locusts': 'cleric',
        'word of recall': 'cleric',
        'blindness': 'cleric',
        'paralyze limb': 'cleric',
        'knit bone': 'cleric',
        'penance': 'theolog',
        'attune': 'theolog',
        'blunt proficiency': 'combat',
        'slash proficiency': 'combat',
        'pierce proficiency': 'combat',
        'barehand proficiency': 'combat',
        'ranged proficiency': 'combat',
        'sharpen': 'combat',
        'smooth': 'combat',
        'tactics': 'advent',
        'bandage': 'advent',
        'ride': 'advent',
        'dissect': 'advent',
        'butcher': 'advent',
        'swim': 'advent',
        'know animal': 'advent',
        'defense': 'advent',
        'know people': 'advent',
        'lumberjack': 'advent',
        'fishing': 'advent',
        'alcoholism': 'advent',
        'offense': 'advent',
        'read magic': 'advent',
        'climbing': 'advent',
        'know veggie': 'advent',
        'sign': 'advent',
        'mend': 'advent',
        'encamp': 'advent',
        'know reptile': 'advent',
        'know giantkin': 'advent',
        'whittle': 'advent',
        'evaluate': 'advent',
        'know other': 'advent',
        'know undead': 'advent',
        'gutter cant': 'advent',
        'gnoll jargon': 'advent',
        'troglodyte pidgin': 'advent',
        'know demon': 'advent',
        'devotion': 'faith',
}

def honed(mud, groups):
    skill = groups[0]
    if 'honing' in mud.state:
        mud.log("Honed {} in {} tries".format(skill, mud.state['honing'][1]))
        del mud.state['honing']

    if skill in honeToType:
        honeType = 'prac ' + honeToType[skill]

    mud.send(honeType)

    if 'hones' not in mud.state:
        mud.state['hones'] = {}
    mud.state['hones'][skill] = time.time()

    if 'hone_on_success' in mud.state:
        mud.state['hone_on_success'](skill)

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

    skill = groups[0]
    learned = groups[1]
    potential = groups[2] if len(groups) >= 3 else 'maxed'
    mud.log('scraped {} at {}/{}'.format(skill, learned, potential))

    mud.state['skillLevels'][skill] = (learned, potential)

ALIASES={
        'sc': 'score',
        '#hones': showHones,
        }

TRIGGERS={
        r'^You are thirsty\.$': 'drink waterskin',
        r'^\*\*\* PRESS RETURN:': '',
        r'^You feel your skills honing in regards to (.+)\.': honed,
        r'^You feel Mezan, the father favoring you more in respects to (.+)\.': honed,
        r'^(.+?)  +Current:  \((.+)\) +Potential:  \((.+)\)': setSkillLevel,
        r'^(.+?)  +Current:  \((.+)\) *': setSkillLevel,
        }


class Sneezy(modular.ModularClient):
    def __init__(self, mud, name):

        self.name = name
        self.logfname = '{}.log.gz'.format(name)
        self.mapfname = 'sneezy.map'

        self.modules = {}
        mods = {
                'eval': (modules.eval.Eval, []),
                # 'repeat': (modules.repeat.Repeat, []),
                'gzlogging': (modules.gzlogging.GzLogging, [self.logfname]),
                'mapper': (modules.mapper.Mapper, [True, self.mapfname, True]),
                }

        for modname, module in mods.items():
            try:
                constructor, args = module
                args = [mud] + args
                self.modules[modname] = constructor(*args)
            except Exception:
                traceback.print_exc()

        super().__init__(mud)

        self.aliases.update(ALIASES)
        self.triggers.update(TRIGGERS)
        with open('passwords_sneezy.json', 'rb') as pws:
            self.triggers.update(json.load(pws))
        self.triggers["Type 'C' to connect with an existing character, or <enter> to see account menu."] = 'c\n' + name
        self.aliases['#autohone ([^,]+), (.+)'] = lambda mud, groups: self.startAutoHone(groups[0], groups[1])
        self.aliases['#killify'] = self.killify

    def killify(self, mud, groups):
        maxLevelsAboveMine = 0
        myLevel = 2
        mobs = self.gmcp['room']['mobs']
        lowLevelMobs = list(filter(lambda x: x['level'] + maxLevelsAboveMine <= myLevel, mobs))
        if not lowLevelMobs:
            self.log('No candidate mobs')
            return
        mob = sorted(lowLevelMobs, key=lambda x: x['level'])[-1]
        mud.send('k {}'.format(mob['name']))

    def startAutoHone(self, skill, cmd):
        self.log("Autohoning {} as {}".format(skill, cmd))
        self.timers['autohone_' + cmd] = self.mktimernow(60*5 + 1, lambda mud: self.honeTimer(skill, cmd))

    def honeTimer(self, skill, cmd):
        def onHoneSuccess(skillHoned):
            if skill == skillHoned:
                # TODO: check for maxed skills
                if skill in self.state['skillLevels'] and self.state['skillLevels'][skill][0] >= 99:
                    self.log("Removing " + skill + " from autohone")
                    del self.timers['autohone_' + cmd]
                else:
                    self.setTimerRemaining('autohone_' + cmd, 301)

        # multi-hone timers need work
        self.state['hone_on_success'] = onHoneSuccess
        self.state['honing'] = (cmd, 1)

    def getHostPort(self):
        return 'sneezymud.org', 7900

def getClass():
    return Sneezy
