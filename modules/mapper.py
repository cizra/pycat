from modules.basemodule import BaseModule
import collections
import json
import os
import pprint
import re
import shutil
import time


def log(*args, **kwargs):
    print(*args, **kwargs)

def roomnr(x):
    # CoffeeMud, Mob Factory exits are negative but room IDs are positive
    return str(abs(x))

# Room IDs are strings (JSON keys must be)
class Map(object):
    def __init__(self, serialized=None):
        if serialized:
            self.m = json.loads(serialized)
            if 'areas' not in self.m:
                self.m['areas'] = {}
        else:
            self.m = {'areas': {}, 'bookmarks': {}, 'rooms': {}}

    def serialize(self):
        return json.dumps(self.m)

    def getBookmarks(self):
        return self.m['bookmarks']

    def setBookmarks(self, bm):
        self.m['bookmarks'] = bm

    def addRoom(self, num, name, data, exits):
        num = str(num)
        self.m['rooms'][num] = {
                'name': name,
                'data': data,
                'exits': exits,
                }

    def roomExists(self, num):
        return num in self.m['rooms']

    def getRoomName(self, num):
        num = str(num)
        return self.m['rooms'][num]['name']

    def getRoomData(self, num):
        num = str(num)
        if num not in self.m['rooms']:
            return {}
        return self.m['rooms'][num]['data']

    def addArea(self, area, room):
        if area not in self.m['areas']:
            self.m['areas'][area] = room

    def setAreaStart(self, area, room):
        self.m['areas'][area] = room

    def getAreas(self):
        return self.m['areas']

    def getRoomCoords(self, num):
        num = str(num)
        # log("Warning: room coords not impl")
        return (0, 0, 0)

    def getRoomExits(self, num):
        num = str(num)
        if num not in self.m['rooms']:
            return {}
        return self.m['rooms'][num]['exits']

    def setExitData(self, source, direction, data):
        self.m['rooms'][source]['exits'][direction]['data'] = data

    def getExitData(self, num, direction):
        num = str(num)
        if 'data' not in self.m['rooms'][num]['exits'][direction]:
            return {}
        return self.m['rooms'][num]['exits'][direction]['data']

    def findRoomsByName(self, name, zone=None):
        out = []
        for num in self.m['rooms']:
            if 'name' in self.m['rooms'][num] and self.m['rooms'][num]['name'] and self.m['rooms'][num]['name'].find(name) != -1 and (not zone or self.m['rooms'][num]['data']['zone'] and zone == self.m['rooms'][num]['data']['zone'] == zone):
                out.append((num, self.m['rooms'][num]['name'], self.m['rooms'][num]['data']['zone']))
        return out

    def findRoomsByZone(self, zone):
        out = []
        for num in self.m['rooms']:
            if 'data' in self.m['rooms'][num] and self.m['rooms'][num]['data'] and 'zone' in self.m['rooms'][num]['data'] and self.m['rooms'][num]['data']['zone'] == zone:
                out.append(num)
        return out

    def delRoom(self, room):
        if room in self.m['rooms']:
            del self.m['rooms'][room]

    def findPath(self, here, there):
        here = str(here)
        there = str(there)
        visited = set()
        paths = {here: []}
        roomq = collections.deque()
        roomq.append(here)
        while roomq:
            room = roomq.popleft()
            if room not in visited:  # A given room might end up in the queue through different paths
                ex = self.m['rooms'][room]['exits']
                for exDir in ex:
                    tgt = ex[exDir]['tgt']
                    paths[tgt] = paths[room] + [exDir]
                    roomq.append(tgt)
                if room == there:
                    return paths[there]
            visited.add(room)


def assemble(cmds1, mode="go"):
    # return ';'.join(paths)
    cmds = []
    for cmd in cmds1:
        cmds += cmd.split(';')

    def direction(elem):
        return elem in ['n', 'e', 's', 'w', 'ne', 'se', 'sw', 'nw', 'u', 'd']

    def runifyDirs(directions):
        if not directions:
            return ""
        count = 1
        # directions hold strings like {n n n e e s}. Transform them to 3n 2e s
        out = ""
        first = True;
        for i in range(1, len(directions)):
            if directions[i - 1] == directions[i]:
                count += 1
            else:
                if first:
                    first = False
                else:
                    out += ' '

                out += ("" if count == 1 else str(count)) + directions[i - 1]
                count = 1
        if not first:
            out += ' '
        out += ("" if count == 1 else str(count)) + directions[-1]
        if len(out) == 1:
            return out;
        else:
            return mode + " " + out;

    out = []
    directions = []  # accumulates directions between non-directions

    while cmds:
        current = cmds[0]
        if direction(current):
            directions.append(current)
            cmds = cmds[1:]
        else:
            if directions:
                out.append(runifyDirs(directions))
                directions = []
            out.append(current)
            cmds = cmds[1:]
    if directions:
        out.append(runifyDirs(directions))
    return ';'.join(out)


class Mapper(BaseModule):
    def help(self, args):
        strs = ["Commands:"]
        for cmd in self.commands.keys():
            strs.append(cmd)
        self.log('\n'.join(strs))

    def current(self):
        return roomnr(self.world.gmcp['room']['info']['num'])

    def currentZone(self):
        return self.m.getRoomData(self.current())['zone']

    def here(self, args):
        if args:
            this = int(args[0])
        else:
            this = self.current()

        bm = None
        for name, dest in self.m.getBookmarks().items():
            if dest == this:
                bm = name
                break

        self.log('\n' + pprint.pformat({
            'num': this,
            'name': self.m.getRoomName(this),
            'data': self.m.getRoomData(this),
            'coords': self.m.getRoomCoords(this),
            'exits': self.m.getRoomExits(this),
            'bookmark': bm,
            }))

    def path2(self, here, there, mode='go'):
        self.log(there)
        if there.isdigit() and int(there) > 0 and 'map-find-result' in self.world.state and len(self.world.state['map-find-result']) >= int(there):
            self.log("Pathing to {}th item = {}".format(int(there)-1, self.world.state['map-find-result'][int(there) - 1][0]))
            there = self.world.state['map-find-result'][int(there) - 1][0]
        elif there in self.m.getBookmarks():
            there = self.m.getBookmarks()[there]
        elif there in self.m.getAreas():
            there = self.m.getAreas()[there]
        else:
            try:
                there = int(there)
            except ValueError:
                self.log("No such bookmark")
                return

        if here == there:
            self.log("Already there!")
            return ''
        then = time.time()
        raw = self.m.findPath(here, there)
        if raw:
            path = assemble(raw, mode)
            self.log("{} (found in {} ms)".format(path, (time.time() - then)*1000))
            return path
        else:
            self.log("Path not found in {} ms".format((time.time() - then)*1000))

    def path(self, there, mode='go'):
        return self.path2(self.current(), there, mode)

    def go(self, room, mode):
        path = self.path(room, mode)
        if path:
            self.send(path.replace(';', '\n'))

    def bookmarks(self, args):
        self.log('Bookmarks:\n' + pprint.pformat(self.m.getBookmarks()))

    def bookmark(self, args):
        arg = ' '.join(args)
        if arg:
            self.m.getBookmarks()[arg] = self.current()
            self.bookmarks([])
        else:
            return self.bookmarks()

    def getExitData(self, source, to):
        return self.m.getExitData(source, to)

    def addExitData(self, source, target, data):
        exd = self.m.getExitData(source, target)
        exd.update(data)
        self.m.setExitData(source, target, exd)

    def draw(self, sizeX=None, sizeY=None):
        # Draw room at x,y,z. Enumerate exits. For each exit target, breadth-first, figure out its new dimensions, rinse, repeat.
        # █▓▒░
        if sizeX and sizeY:
            columns, lines = sizeX, sizeY
        else:
            columns, lines = shutil.get_terminal_size((21, 22))

        def adjustExit(x, y, d, prev):
            m = re.match(r'open .+;(.+)', d)
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
        startX, startY, startZ = (0, 0, 0)  # self.m.getRoomCoords(self.current())
        centerX, centerY = (columns-1)//2, (lines-1)//2
        data = self.m.getRoomData(self.current())
        area = data['zone']

        roomq = collections.deque()
        roomq.append((centerX, centerY, self.current()))

        visited = set()

        def getExitLen(source, to):
            exitData = self.getExitData(source, to)
            if not exitData or 'len' not in exitData:
                return 0
            return int(exitData['len'] * 2)

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
                    tgt = tgt['tgt']
                    if d in ['n', 'e', 's', 'w', 'u', 'd', 'ne', 'se', 'sw', 'nw'] or re.match(r'open .+;[neswud]+', d):
                        dataD = self.m.getRoomData(tgt)
                        exists = False
                        nextArea = None
                        if dataD:
                            exists = True
                            nextArea = dataD['zone'] if 'zone' in dataD else None
                        sameAreas = self.drawAreas or nextArea == area

                        if not exists or not sameAreas:
                            exitLen = 1
                        else:
                            exitLen = getExitLen(room, d) + 1

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
                                # print("Offset detected:", roomX - tgtX, roomY-tgtX)
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
        if 'visited' not in self.world.state:
            self.world.state['visited'] = set()
        self.log("Visited {} rooms today!".format(len(self.world.state['visited'])))

    def save(self, args):
        if len(args) == 1:
            self.mapfname = args[0]
        with open(self.mapfname, 'w') as f:
            f.write(self.m.serialize())
        self.log("Serialized map to", self.mapfname)

    def startExit(self, args):
        self.exitKw = ' '.join(args)
        nr = roomnr(self.world.gmcp['room']['info']['num'])
        room = self.world.gmcp['room']['info']
        self.exitFrom = {}
        self.exitFrom['exits'] = {}
        self.exitFrom['id'] = nr
        self.exitFrom['name'] = room['name']
        self.exitFrom['data'] = dict(zone=room['zone'], terrain = room['terrain'])
        exits = {}
        for k, v in room['exits'].items():
            self.exitFrom['exits'][k.lower()] = {'tgt': roomnr(v)}
        self.log("Type '#map endexit' when you're in the right room, or #map endexit abort")
        self.exitKw = self.exitKw.replace(';', '\n')
        self.exitKw = self.exitKw.replace('~', '\n')
        self.log("Exit: " + repr(self.exitKw))
        self.send(self.exitKw)

    def endExit(self, args):
        if len(args) == 1:
            self.log("Aborted.")
            return
        self.exitFrom['exits'][self.exitKw] = {'tgt': self.current()}
        self.m.addRoom(
                self.exitFrom['id'],
                self.exitFrom['name'],
                self.exitFrom['data'],
                self.exitFrom['exits'])
        self.exitKw = None
        self.log("Done.")

    def lockExit(self, args):
        direction, level = args if len(args) > 1 else (args[0], -1)
        tgt = self.getRoomByDirection(direction)
        if not tgt:
            self.mud.log("Exit doesn't exist")
            return
        self.addExitData(self.current(), direction, {'lock': int(level)})
        return self.here([self.current()])

    def startRoom(self, args):
        self.m.setAreaStart(self.currentZone(), self.current())

    def getRoomByDirection(self, direction):
        here = self.current()
        exits = self.m.getRoomExits(here)
        if direction.lower() not in exits:
            self.log("No such direction")
            return None
        return exits[direction.lower()]['tgt']

    def exitLen(self, direction, increment):
        here = self.current()
        there = self.getRoomByDirection(direction)

        def do(here, there):
            exits = self.m.getRoomExits(here)
            for dir, tgt in exits.items():
                if tgt['tgt'] == there:
                    data = self.m.getExitData(here, dir)
                    if 'len' not in data:
                        data['len'] = 0
                    data['len'] += increment
                    if data['len'] <= 0:
                        data['len'] = 0
                    self.m.setExitData(here, dir, data)
                    break

        do(here, there)
        do(there, here)
        self.show(self.draw())

    def inc(self, args):
        self.exitLen(args[0], 1)

    def dec(self, args):
        self.exitLen(args[0], -1)

    def load(self, args):
        # TODO: memory usage and map size can be reduced by storing
        # terrains/zones in mapdata, and referencing them by index in rooms 
        if len(args) == 1:
            self.mapfname = args[0]
        try:
            with open(self.mapfname, 'r') as f:
                ser = f.read()
            self.m = Map(ser)
            print("Loaded map from", self.mapfname)
        except FileNotFoundError:
            self.m = Map()
            print("Created a new map")

    def find(self, args):
        res = self.world.state['map-find-result'] = self.m.findRoomsByName(' '.join(args))
        res.sort(key=lambda x: x[1])
        res.sort(key=lambda x: x[2])
        count = 1
        for nr, name, area in res:
            self.show("{count}\t{nr}\t{name}\t\t{area}\n".format(count=count, nr=nr, name=name, area=area))
            count += 1

    def currentArea(self):
        return self.m.getRoomData(self.current())['zone']

    def unmapped(self, unvisited, inArea, one):
        if 'visited' not in self.world.state:
            self.world.state['visited'] = set()
        out = []  # A set would probably be smaller, but a list is in the order of closeness.
        visited = set()
        roomq = collections.deque()
        roomq_check = set([self.current()])  # prevent enqueuing the same room a zillon times
        roomq.append(self.current())
        visited.add(self.current())
        startArea = self.currentArea()
        while roomq:
            room = roomq.popleft()
            roomq_check.remove(room)
            visited.add(room)
            exits = self.m.getRoomExits(room)
            for d, tgt in exits.items():
                tgt = tgt['tgt']
                edata = self.m.getExitData(room, d)
                rdata = self.m.getRoomData(tgt)
                if 'lock' not in edata:
                    if not rdata:  # unexplored
                        if one:
                            return [tgt]
                        else:
                            out.append(tgt)
                    else:
                        sameZone = not inArea or rdata['zone'] == startArea
                        if (unvisited and tgt not in self.world.state['visited'] and sameZone):
                            out.append(tgt)
                        else:
                            if tgt not in visited and sameZone and tgt not in roomq_check:
                                roomq_check.add(tgt)
                                roomq.append(tgt)
        return list(dict.fromkeys(out))  # dedupe

    def autoVisit(self, args=None):
        if not args or args[0] != 'exit':
            self.world.state['autoVisitArea'] = self.currentArea()
        if args and args[0] == 'stop':
            del self.world.state['autoVisitTarget'] 
            del self.world.state['autoVisitArea'] 
            self.log("Stopped autovisit")
            return
        unmapped = self.unmapped(False, 'autoVisitArea' in self.world.state, True)
        if unmapped:
            self.world.state['autoVisitTarget'] = unmapped[0]
            self.log("Visiting " + unmapped[0])
            self.go(self.world.state['autoVisitTarget'], 'go')
        else:
            self.log("Done!")

    def areas(self, args):
        for name in sorted(self.m.getAreas().keys()):
            num = self.m.getAreas()[name]
            self.show("{}\t{}\n".format(num, name))

    def delExits(self, args):
        value = self.world.gmcp['room']['info']
        id = roomnr(value['num'])
        data = dict(zone=value['zone'], terrain = value['terrain'])
        name = value['name']
        self.m.addRoom(id, name, data, {})

    def delZone(self, args):
        if args:
            zone = ' '.join(args)
        else:
            zone = self.currentZone()
        self.log("Deleting " + zone)
        rooms = self.m.findRoomsByZone(zone)
        self.log(rooms)
        for room in rooms:
            self.m.delRoom(room)
        self.log(zone + " deleted")

    def __init__(self, mud, drawAreas, mapfname, spacesInRun=True):
        super().__init__(mud)
        self.drawAreas = drawAreas
        self.spacesInRun = spacesInRun
        self.load([mapfname])

        self.commands = {
                'lock': self.lockExit,
                'unmapped': lambda args: self.log('\n' + '\n'.join([str(i) for i in self.unmapped(False, True, False)])),
                'unvisited': lambda args: self.log('\n' + '\n'.join([str(i) for i in self.unmapped(True, True, False)])),
                'gounmapped': lambda args: self.go(self.unmapped(False, True, True)[0], 'go'),
                'av': self.autoVisit,
                'areas': self.areas,
                'find': self.find,
                'load': self.load,
                'read': self.load,
                'help': self.help,
                'here': self.here,
                'add': self.bookmark,
                'bookmark': self.bookmark,
                'name': self.bookmark,
                'bookmarks': self.bookmarks,
                'path': lambda args: self.path(' '.join(args), 'go'),
                'go': lambda args: self.go(' '.join(args), 'go'),
                'run': lambda args: self.go(' '.join(args), 'run'),
                'save': self.save,
                'write': self.save,
                'startexit': self.startExit,
                'endexit': self.endExit,
                'inc': self.inc,
                'dec': self.dec,
                'delexits': self.delExits,
                'delzone': self.delZone,
                'dump': lambda args: self.log(self.m.m),
                'startroom': self.startRoom,
                }

        # for creating custom exits
        self.exitKw = None
        self.exitFrom = None

    def alias(self, line):
        words = line.split(' ')

        if words[0].lower() != '#map':
            return

        if len(words) == 1:
            self.show(self.draw())
            return True

        cmd = words[1]
        if cmd in self.commands:
            self.commands[cmd](words[2:])
        else:
            self.help(words[2:])
        return True

    def handleGmcp(self, cmd, value):
        # CoffeeMUD's room.info
        # {'coord': {'cont': 0, 'id': 0, 'x': -1, 'y': -1},
        #   'desc': '',
        #   'details': '',
        #   'exits': {'N': -565511209},
        #   'id': 'Homes#1226',
        #   'name': 'An empty room',
        #   'num': -565511180,
        #   'terrain': 'cave',
        #   'zone': 'Homes'}

        # SneezyMUD's room.info
        # {'coord': {'cont': 0, 'id': -1, 'x': -1, 'y': -1},
        #  'details': '',
        #  'exit_kw': {'s': 'door'},
        #  'exits': {'e': 753, 'n': 757, 's': 114, 'w': 751},
        #  'name': 'Church Entry',
        #  'num': 752,
        #  'terrain': 'Temperate Building',
        #  'zone': '13'}


        if cmd == 'room.info':
            id = roomnr(value['num'])
            if 'visited' not in self.world.state:
                self.world.state['visited'] = set()
            self.world.state['visited'].add(id)
            name = value['name']
            self.m.addArea(value['zone'], id)
            data = dict(zone=value['zone'], terrain = value['terrain'])
            exits = self.m.getRoomExits(id)  # retain custom exits
            for direction, target in value['exits'].items():
                tgt = roomnr(target)
                dir = direction.lower()
                if dir not in exits:
                    exits[dir] = {'tgt': tgt}
                if not self.m.roomExists(tgt):  # doesn't exist yet, insert stub for easy pathfinding 
                    self.m.addRoom(tgt, None, {}, {})
            if 'exit_kw' in value:
                for direction, door in value['exit_kw'].items():
                    exits['open {door} {direction};{direction}'.format(door=door, direction=direction)] = exits[direction.lower()]
            self.m.addRoom(id, name, data, exits)

            if 'autoVisitTarget' in self.world.state and self.world.state['autoVisitTarget'] == id:
                if 'char' in self.world.gmcp and self.world.gmcp['char']['vitals']['moves'] < 60:
                    self.log("Autovisiting, but near out of moves")
                elif 'autoVisitArea' in self.world.state and self.world.state['autoVisitArea'] != self.currentArea():
                    self.log("Autovisiting, but changed areas")
                else:
                    self.autoVisit(['exit'] if 'autoVisitArea' not in self.world.state else None)
            # self.show(self.draw())
