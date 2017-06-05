from modules.basemodule import BaseModule
import mapper.libmapper
import pprint
import re
import time


class Mapper(BaseModule):
    def __init__(self, mud, mapfname='default.map'):
        self.mapfname = mapfname
        try:
            with open(self.mapfname, 'r') as f:
                ser = f.read()
            self.m = mapper.libmapper.Map(ser)
        except FileNotFoundError:
            self.m = mapper.libmapper.Map()
        super().__init__(mud)

    def quit(self):
        with open(self.mapfname, 'w') as f:
            f.write(self.m.serialize())
        self.log("Serialized map to ", self.mapfname)

    def current(self):
        return self.gmcp['room']['info']['num']

    def path(self, there):
        here = self.current()
        if here == there:
            self.log("Already there!")
            return ''
        then = time.time()
        path = self.m.findPath(here, there)
        self.log("{} (found in {} seconds)".format(path, time.time() - then))
        return path

    def alias(self, line):
        words = line.split(' ')
        if words[0] != '#map':
            return
        cmd = words[1]
        if cmd == 'here':
            here = self.current()
            self.log('\n' + pprint.pformat({
                'num': here,
                'name': self.m.getRoomName(here),
                'zone': self.m.getRoomZone(here),
                'terrain': self.m.getRoomTerrain(here),
                'coords': self.m.getRoomCoords(here),
                'exits': self.m.getRoomExits(here),
                }))
            return True
        elif re.match(r'#map path ([^ ]+)', line):
            there = int(re.match(r'#map path ([^ ]+)', line).group(1))
            self.log(self.path(there))
            return True
        elif re.match(r'#map go ([^ ])', line):
            there = int(re.match(r'#map path ([^ ]+)', line).group(1))
            self.send(self.path(there))
            return True

    def trigger(self, raw, stripped):
        pass

    def handleGmcp(self, cmd, value):
        # room.info {'details': '', 'id': 'Homes#1226', 'terrain': 'cave', 'exits': {'N': -565511209}, 'coord': {'id': 0, 'x': -1, 'cont': 0, 'y': -1}, 'desc': '', 'num': -565511180, 'name': 'An empty room', 'zone': 'Homes'}
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
            zone = value['zone']
            terrain = value['terrain']
            exits = {}
            for k, v in value['exits'].items():
                exits[k.lower()] = v
            self.m.addRoom(id, name, zone, terrain, exits)
