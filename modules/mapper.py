from modules.basemodule import BaseModule
import mapper.libmapper
import pprint
import re
import time
import json


class Mapper(BaseModule):
    def help(self, args):
        strs = ["Commands:"]
        for cmd in self.commands.keys():
            strs.append(cmd)
        self.log('\n'.join(strs))

    def current(self):
        return self.gmcp['room']['info']['num']

    def here(self, args):
        if args:
            this = int(args[0])
        else:
            this = self.current()
        self.log('\n' + pprint.pformat({
            'num': this,
            'name': self.m.getRoomName(this),
            'data': self.m.getRoomData(this),
            'coords': self.m.getRoomCoords(this),
            'exits': self.m.getRoomExits(this),
            }))

    def path(self, args):
        there = args[0]
        if there in self.data['bookmarks']:
            there = self.data['bookmarks'][there]
        else:
            there = int(there)

        this = self.current()
        if this == there:
            self.log("Already there!")
            return ''
        then = time.time()
        path = self.m.findPath(this, there)
        self.log("{} (found in {} seconds)".format(path, time.time() - then))
        return path

    def go(self, args):
        self.send(self.path(args).replace(';', '\n'))

    def bookmarks(self, args):
        self.log('Bookmarks:\n' + pprint.pformat(self.data['bookmarks']))

    def bookmark(self, args):
        arg = ' '.join(args)
        self.data['bookmarks'][arg] = self.current()
        self.bookmarks([])

    def draw(self):
        self.log("""
█ █ █
│ │ │
▒─▒╫▒╸
│ │ │
▓ ▓ ▓
""")

    def quit(self):
        self.m.setMapData(json.dumps(self.data))
        with open(self.mapfname, 'w') as f:
            f.write(self.m.serialize())
        self.log("Serialized map to ", self.mapfname)

    def __init__(self, mud, mapfname='default.map'):
        self.mapfname = mapfname
        try:
            with open(self.mapfname, 'r') as f:
                ser = f.read()
            self.m = mapper.libmapper.Map(ser)
            self.data = json.loads(self.m.getMapData())
        except FileNotFoundError:
            self.data = {
                    'bookmarks': {},
                    }
            self.m = mapper.libmapper.Map()

        self.commands = {
                'help': self.help,
                'here': self.here,
                'bookmark': self.bookmark,
                'bookmarks': self.bookmarks,
                'path': self.path,
                'go': self.go,
                'save': lambda: self.quit([])
                }

        super().__init__(mud)

    def alias(self, line):
        words = line.split(' ')

        if words[0] != '#map':
            return

        if len(words) == 1:
            self.draw()
            return True

        cmd = words[1]
        if cmd in self.commands:
            self.commands[cmd](words[2:])
        else:
            self.help(words[2:])
        return True

    def handleGmcp(self, cmd, value):
        # room.info
        # {'coord': {'cont': 0, 'id': 0, 'x': -1, 'y': -1},
        #   'desc': '',
        #   'details': '',
        #   'exits': {'N': -565511209},
        #   'id': 'Homes#1226',
        #   'name': 'An empty room',
        #   'num': -565511180,
        #   'terrain': 'cave',
        #   'zone': 'Homes'}
        if cmd == 'room.info':
            id = value['num']
            name = value['name']
            data = dict(zone=value['zone'], terrain = value['terrain'])
            exits = {}
            for k, v in value['exits'].items():
                exits[k.lower()] = v
            self.m.addRoom(id, name, json.dumps(data), exits)
