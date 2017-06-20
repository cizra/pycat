from modules.basemodule import BaseModule
import mapper.libmapper
import collections
import json
import os
import pprint
import re
import shutil
import time


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

        just_exits = self.m.getRoomExits(this)
        exits = {}
        for dir, tgt in just_exits.items():
            data = self.m.getExitData(this, tgt)
            data = json.loads(data) if data else {}
            exits[dir] = {'dst': tgt, 'data': data}

        self.log('\n' + pprint.pformat({
            'num': this,
            'name': self.m.getRoomName(this),
            'data': self.m.getRoomData(this),
            'coords': self.m.getRoomCoords(this),
            'exits': exits,
            }))

    def path(self, there):
        if there in self.data['bookmarks']:
            there = self.data['bookmarks'][there]
        else:
            try:
                there = int(there)
            except ValueError:
                self.log("No such bookmark")
                return

        this = self.current()
        if this == there:
            self.log("Already there!")
            return ''
        then = time.time()
        path = self.assemble(self.m.findPath(this, there))
        self.log("{} (found in {} ms)".format(path, (time.time() - then)/1000))
        return path

    def go(self, room):
        path = self.path(room)
        if path:
            self.send(path.replace(';', '\n'))

    def bookmarks(self, args):
        self.log('Bookmarks:\n' + pprint.pformat(self.data['bookmarks']))

    def bookmark(self, args):
        arg = ' '.join(args)
        self.data['bookmarks'][arg] = self.current()
        self.bookmarks([])

    def draw(self, sizeX=None, sizeY=None):
        # Draw room at x,y,z. Enumerate exits. For each exit target, breadth-first, figure out its new dimensions, rinse, repeat.
        # █▓▒░
        if sizeX and sizeY:
            columns, lines = sizeX, sizeY
        else:
            columns, lines = shutil.get_terminal_size((21, 22))

        def adjustExit(x, y, d, prev):
            m = re.match(r'open (.);.', d)
            if m:
                return adjustExit(x, y, m.group(1), prev)
            if d == 'n':
                return x, y-1, '│', '↑', '║'
            if d == 'w':
                return x-1, y, '─', '←', '═'
            if d == 's':
                return x, y+1, '│', '↓', '║'
            if d == 'e':
                return x+1, y, '─', '→', '═'
            if d == 'd':
                if prev == '▲':
                    return x, y, '◆', '◆', '◆'
                else:
                    return x, y, '▼', '▼', '▼'
            if d == 'u':
                if prev == '▼':
                    return x, y, '◆', '◆', '◆'
                else:
                    return x, y, '▲', '▲', '▲'
            if d == 'nw':
                return x-1, y-1, '\\', '\\', '\\'
            if d == 'sw':
                return x-1, y+1, '/', '/', '/'
            if d == 'se':
                return x+1, y+1, '\\', '\\', '\\'
            if d == 'ne':
                return x+1, y-1, '/', '/', '/'

        out = []  # NB! indices are out[y][x] because the greater chunks are whole lines
        for _ in range(lines - 1):  # -1 for the next prompt
            out.append([' '] * columns)

        # The only room coordinates that matter are the start room's -- the rest get calculated by tracing paths.
        startX, startY, startZ = self.m.getRoomCoords(self.current())
        centerX, centerY = (columns-1)//2, (lines-1)//2
        data = self.m.getRoomData(self.current())
        area = json.loads(data)['zone']

        roomq = collections.deque()
        roomq.append((centerX, centerY, self.current()))

        visited = set()

        def getExitLen(source, target):
            exitDataS = self.m.getExitData(source, target)
            if not exitDataS:
                return 1
            exitData = json.loads(exitDataS)
            if not exitData or 'len' not in exitData:
                return 1
            return int(exitData['len'])

        def fits(x, y):
            return 0 <= x and x < columns and 0 <= y and y < lines-1

        # TODO: one-way exits
        # TODO: draw doors
        coordCache = {}  # Remember where we drew each room, to search for broken-looking exits
        while roomq:
            drawX, drawY, room = roomq.popleft()
            if room not in visited:  # A given room might end up in the queue through different paths
                mapX, mapY, mapZ = self.m.getRoomCoords(room)
                visited.add(room)
                # It's possible to keep walking through z layers and end up back on z=initial, which might produce nicer maps -- but we'll have to walk the _whole_ map, or bound by some range.
                out[drawY][drawX] = '█'
                coordCache[room] = (drawX, drawY)
                # out[drawY][drawX] = str(count % 10)
                # count += 1
                exits = self.m.getRoomExits(room)
                for d, tgt in exits.items():
                    if d in ['n', 'e', 's', 'w', 'u', 'd', 'ne', 'se', 'sw', 'nw'] or re.match(r'open .;.', d):
                        dataS = self.m.getRoomData(tgt)
                        exists = dataS != ''
                        dataD = json.loads(dataS) if exists else {}
                        nextArea = dataD['zone'] if 'zone' in dataD else None
                        sameAreas = self.drawAreas or nextArea == area

                        if not exists or not sameAreas:
                            exitLen = 1
                        else:
                            exitLen = getExitLen(room, tgt)

                        exX = drawX
                        exY = drawY

                        roomX, roomY = exX, exY
                        # Figure out the coordinates of the target room
                        for _ in range(exitLen + 1):  # exitlen for the exit, +1 for the target room
                            roomX, roomY, _, _, _ = adjustExit(roomX, roomY, d, ' ')

                        # Mark exits that break map (if the target room is already drawn, but not adjacent to this one)
                        mark = False
                        if tgt in visited:
                            tgtX, tgtY = coordCache[tgt]
                            if tgtX != roomX or tgtY != roomY:
                                print("Offset detected:", roomX - tgtX, roomY-tgtX)
                                mark = True

                        # draw a long exit for beautification
                        for _ in range(exitLen):
                            exX, exY, regularExit, hiddenExit, markedExit = adjustExit(exX, exY, d, out[drawY][drawX])
                            if fits(exX, exY):
                                # If the map grid element we'd occupy is already occupied, don't go there
                                nextX, nextY, _, _, _ = adjustExit(exX, exY, d, ' ')  # Adjust again, ie. go one step further in the same direction for the target room
                                # Don't overwrite already drawn areas
                                free = fits(exX, exY) and (not fits(nextX, nextY) or out[nextY][nextX] == ' ') or tgt in visited

                                if mark:
                                    out[exY][exX] = markedExit
                                elif free and exists and sameAreas:
                                    out[exY][exX] = regularExit
                                else:
                                    out[exY][exX] = hiddenExit

                        visit = (exists
                                and tgt not in visited
                                and sameAreas
                                and d not in ['u', 'd']
                                and fits(roomX, roomY)
                                and out[roomY][roomX] == ' '
                                )
                        if visit:
                            roomq.append((roomX, roomY, tgt))

        # Special marking for start room:
        if out[centerY][centerX] == '▼':
            out[centerY][centerX] = '▿'
        elif out[centerY][centerX] == '▲':
            out[centerY][centerX] = '▵'
        elif out[centerY][centerX] == '◆':
            out[centerY][centerX] = '◇'
        else:
            out[centerY][centerX] = '░'

        outlines = [''.join(char) for char in out]
        outstr = ""
        for l in outlines:
            if l.strip(' '):
                outstr += l + '\n'
        return outstr

    def quit(self, args=None):
        self.save([self.mapfname])

    def save(self, args):
        if len(args) == 1:
            self.mapfname = args[0]
        self.m.setMapData(json.dumps(self.data))
        with open(self.mapfname, 'w') as f:
            f.write(self.m.serialize())
        self.log("Serialized map to", self.mapfname)

    def startExit(self, args):
        self.exitKw = ' '.join(args)
        room = self.gmcp['room']['info']
        self.exitFrom = {}
        self.exitFrom['exits'] = {}
        self.exitFrom['id'] = room['num']
        self.exitFrom['name'] = room['name']
        self.exitFrom['data'] = dict(zone=room['zone'], terrain = room['terrain'])
        exits = {}
        for k, v in room['exits'].items():
            self.exitFrom['exits'][k.lower()] = v
        self.log("Type '#map endexit' when you're in the right room, or #map endexit abort")
        self.send(self.exitKw.replace(';', '\n'))

    def endExit(self, args):
        if len(args) == 1:
            self.log("Aborted.")
            return
        self.exitFrom['exits'][self.exitKw] = self.current()
        self.m.addRoom(
                self.exitFrom['id'],
                self.exitFrom['name'],
                json.dumps(self.exitFrom['data']),
                self.exitFrom['exits'])
        self.exitKw = None

    def getRoomByDirection(self, direction):
        here = self.current()
        exits = self.m.getRoomExits(here)
        if direction.lower() not in exits:
            self.log("No such direction")
            return None
        return exits[direction.lower()]

    def exitLen(self, direction, increment):
        here = self.current()
        there = self.getRoomByDirection(direction)

        def do(here, there):
            data = self.m.getExitData(here, there)
            if data:
                data = json.loads(data)
            else:
                data = {}
            # Oops, must have stored it as string :( TODO: correct in files and remove this code

            data['len'] = int(data['len']) if 'len' in data else 1
            data['len'] += increment
            if data['len'] <= 1:
                data['len'] = 1
            self.m.setExitData(here, there, json.dumps(data))

        do(here, there)
        do(there, here)
        print(self.draw())

    def inc(self, args):
        self.exitLen(args[0], 2)

    def dec(self, args):
        self.exitLen(args[0], -2)

    def load(self, args):
        # TODO: memory usage and map size can be reduced by storing
        # terrains/zones in mapdata, and referencing them by index in rooms 
        if len(args) == 1:
            self.mapfname = args[0]
        try:
            with open(self.mapfname, 'r') as f:
                ser = f.read()
            self.m = mapper.libmapper.Map(ser)
            print("Loaded map from", self.mapfname)
        except FileNotFoundError:
            self.m = mapper.libmapper.Map()
            print("Created a new map")

        md = self.m.getMapData()
        if md:
            self.data = json.loads(self.m.getMapData())
        else:
            self.data = {
                    'bookmarks': {},
                    }

    def find(self, args):
        self.log('\n' + pprint.pformat(self.m.findRoomByName(args[0])))

    def unmapped(self, args):
        out = []  # A set would probably be smaller, but a list is in the order of closeness.
        visited = set()
        roomq = collections.deque()
        roomq.append(self.current())
        visited.add(self.current())
        startArea = json.loads(self.m.getRoomData(self.current()))['zone']
        while roomq:
            room = roomq.popleft()
            visited.add(room)
            exits = self.m.getRoomExits(room)
            for d, tgt in exits.items():
                dataS = self.m.getRoomData(tgt)
                if not dataS:
                    out.append(tgt)
                else:
                    if  tgt not in visited and json.loads(dataS)['zone'] == startArea:
                        roomq.append(tgt)
        return list(dict.fromkeys(out))  # dedupe


    def assemble(self, paths):
        return ';'.join(paths)

    def __init__(self, mud, drawAreas, mapfname, spaces):
        self.drawAreas = drawAreas
        self.spaces = spaces
        self.load([mapfname])

        self.commands = {
                'unmapped': lambda args: self.log('\n' + '\n'.join([str(i) for i in self.unmapped(args)])),
                'gounmapped': lambda args: self.go(self.unmapped(args).pop()),
                'find': self.find,
                'load': self.load,
                'read': self.load,
                'help': self.help,
                'here': self.here,
                'bookmark': self.bookmark,
                'name': self.bookmark,
                'bookmarks': self.bookmarks,
                'path': lambda args: self.path(args[0]),
                'go': lambda args: self.go(args[0]),
                'save': self.save,
                'write': self.save,
                'startexit': self.startExit,
                'endexit': self.endExit,
                'inc': self.inc,
                'dec': self.dec,
                }

        # for creating custom exits
        self.exitKw = None
        self.exitFrom = None

        super().__init__(mud)

    def alias(self, line):
        words = line.split(' ')

        if words[0] != '#map':
            return

        if len(words) == 1:
            print(self.draw())
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
            exits = self.m.getRoomExits(id)  # retain custom exits
            for k, v in value['exits'].items():
                exits[k.lower()] = v
            self.m.addRoom(id, name, json.dumps(data), exits)

            with open('mapdraw', 'w') as f:
                f.write(self.draw(35, 35) + '\n')
