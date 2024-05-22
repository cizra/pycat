from modules.basemodule import BaseModule
import collections
import json
import os
import pprint
import re
import shutil
import time


def roomnr(x):
    # CoffeeMud, Mob Factory exits are negative but room IDs are positive
    return str(abs(x))

def nothing(*args, **kwargs):
    pass

reverse = {
        'n': 's',
        'e': 'w',
        's': 'n',
        'w': 'e',
        'u': 'd',
        'd': 'u'
        }

def isMaze(roomId):
    return re.match(r'[^#]+#\d+#\(\d+,\d+\)$', roomId) != None  # CoffeeMUD mazes are described with just one room ID + coords: Sewers#7019#(9,5)

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

    def delBookmark(self, name):
        del self.m['bookmarks'][name]

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

    def getRoomArea(self, num):
        num = str(num)
        room = self.m['rooms'].get(num)
        if not room:
            return None
        data = room.get('data')
        if not data:
            return None
        return data.get('zone')

    def addArea(self, area, room):
        if area not in self.m['areas']:
            self.m['areas'][area] = room

    def setAreaStart(self, area, room):
        self.m['areas'][area] = room

    def getAreas(self):
        return self.m['areas']

    def getRoomCoords(self, num):
        num = str(num)
        return (
            self.m['rooms'][num]['coords']['x'] if 'coords' in self.m['rooms'][num] else 0,
            self.m['rooms'][num]['coords']['y'] if 'coords' in self.m['rooms'][num] else 0,
            self.m['rooms'][num]['coords']['z'] if 'coords' in self.m['rooms'][num] else 0
        )

    def setRoomCoords(self, num, x, y, z):
        num = str(num)
        self.m['rooms'][num]['coords'] = dict(x=x, y=y, z=z)

    def getRoomExits(self, num):
        num = str(num)
        if num not in self.m['rooms']:
            return {}
        return self.m['rooms'][num]['exits']

    def setExitData(self, source, direction, data):
        if data:
            self.m['rooms'][source]['exits'][direction]['data'] = data
        else:
            del self.m['rooms'][source]['exits'][direction]['data']

    def getExitData(self, num, direction):
        num = str(num)
        if 'data' not in self.m['rooms'][num]['exits'][direction]:
            return {}
        return self.m['rooms'][num]['exits'][direction]['data']

    def findRoomsByName(self, name, zone=None):
        return self.findRoomsBy(lambda x: x.get('name'), name, zone)

    def findRoomsById(self, desiredId, desiredZone=None):
        return self.findRoomsBy(lambda x: x['data'].get('id') if 'data' in x else None, desiredId, desiredZone)

    def findRoomsBy(self, keySelector, desiredValue, desiredZone=None):
        out = []
        for num, room in self.m['rooms'].items():
            data = room.get('data')
            if not data:
                continue
            value = keySelector(room)
            if not value:
                continue
            if value.find(desiredValue) == -1:
                continue
            zone = data.get('zone')
            if desiredZone:
                if zone != desiredZone:
                    continue
            out.append((num, "{}:\t{}".format(data.get('id', 'no-id'), room.get('name')), zone))
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


    def isLocked(self, exit):
        if 'data' not in exit:
            return False
        if 'lock' not in exit['data']:
            return False
        return True  # TODO: check level

    def isHardLocked(self, exit):
        if 'data' not in exit:
            return False
        if 'hardLock' not in exit['data']:
            return False
        return True  # TODO: check level

    # visitRoom returs None to continue search, a value for end condition (like path to desired room).
    # visitExit returns True if we should stop BFSing after this exit.
    def bfs(self, here, visitRoom, visitExit, bypassLocks, enterMazes=False, swim=False):
        visited = set()
        roomq = collections.deque()
        roomq.append(here)
        while roomq:
            room = roomq.popleft()
            # Some are mazes, some are grid-type rooms, pathable through. Need a better way to mark mazes - just locks?
            # if not enterMazes and isMaze((self.m['rooms'][room].get('data', {}) or {}).get('id') or ''):
            #     continue
            if not bypassLocks and not swim and ((self.m['rooms'][room].get('data', {}) or {}).get('terrain') or '') == 'watersurface':
                continue
            if room not in visited:  # A given room might end up in the queue through different paths
                ex = self.m['rooms'][room]['exits']
                for exDir in ex:
                    if not bypassLocks and self.isLocked(ex[exDir]):
                        print("Bypassing {} as locked".format(room))
                        continue
                    # TODO: add options to path through swim-only rooms, etc
                    if not bypassLocks and ex[exDir].get('data', {}).get('swim'):  # rendundant with the 'watersurface' check above? Regardless, useful for softlocking unexplored exits
                        print("Bypassing {} as swim".format(room))
                        continue
                    if not bypassLocks and ex[exDir].get('data', {}).get('crawl'):
                        print("Bypassing {} as crawl".format(room))
                        continue
                    if not bypassLocks and ex[exDir].get('data', {}).get('climb'):
                        print("Bypassing {} as climb".format(room))
                        continue
                    if not bypassLocks and ex[exDir].get('data', {}).get('fly'):
                        print("Bypassing {} as fly".format(room))
                        continue

                    if self.isHardLocked(ex[exDir]):
                        continue
                    tgt = ex[exDir]['tgt']
                    if not visitExit(room, exDir, tgt):
                        roomq.append(tgt)
                res = visitRoom(room)
                if res is not None:
                    return res
                visited.add(room)

    def findPath(self, here, there, bypassLocks=False):
        here = str(here)
        there = str(there)
        paths = {here: []}

        def visitRoom(room):
            if room == there:
                return paths[there]

        def visitExit(room, exDir, tgt):
            paths[tgt] = paths[room] + [exDir]

        return self.bfs(here, visitRoom, visitExit, bypassLocks)

    def areaConnectionsGraph(self):
        excluded = set(["Thrystryn Transportation", "Zolo`s Store"])
        here = '496521296' # start from Midgaard recall
        area1 = self.m['rooms'][here]['data']['zone']  # Midgaard
        connections = set()

        def visitRoom(room):
            area2 = self.getRoomArea(room)
            if area2 and area1 != area2:
                if (area2, area1) not in connections:
                    if area1 not in excluded and area2 not in excluded:
                        connections.add((area1, area2))

        return self.bfs(here, visitRoom, nothing, bypassLocks=True)

        # A digraph would be more accurate, but it looks very busy
        with open("areaconnections.dot", "w") as f:
            f.write("strict graph {\n")
            for elem in connections:
                f.write('"')
                f.write(elem[0])
                f.write('" -- "')
                f.write(elem[1])
                f.write('"')
                f.write("\n")
            f.write("}")

    def nearbyAreas(self, here, withPath):
        area1 = self.getRoomArea(here)
        nearbyAreas = {}
        paths = {here: []}

        def visitExit(room, exDir, tgt):
            paths[tgt] = path = paths[room] + [exDir]
            area2 = self.getRoomArea(tgt)
            if not area2: # unmapped
                return True
            if area1 != area2:
                if area2 not in nearbyAreas:
                    nearbyAreas[area2] = len(path), assemble(path, 'go')
                return True

        self.bfs(here, nothing, visitExit, bypassLocks=True)

        if not nearbyAreas:
            return ['None', (0, '')]
        if withPath:
            return list(map(lambda kvp: "{}: {}".format(kvp[0], kvp[1][1]), sorted(nearbyAreas.items(), key=lambda x: x[1][0])))
        else:
            return list(map(lambda kvp: kvp[0], sorted(nearbyAreas.items(), key=lambda x: x[1][0])))


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

    def path2(self, here, there, mode='go', bypassLocks=False):
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
        raw = self.m.findPath(here, there, bypassLocks)
        if raw:
            path = assemble(raw, mode)
            self.log("{} (found in {} ms)".format(path, (time.time() - then)*1000))
            return path
        else:
            self.log("Path not found in {} ms".format((time.time() - then)*1000))

    def path(self, there, mode='go', bypassLocks=False):
        return self.path2(self.current(), there, mode, bypassLocks)

    def go(self, room, mode, bypassLocks=False):
        path = self.path(room, mode, bypassLocks)
        if path:
            self.send(path.replace(';', '\n'))

    def filterByArgs(self, bookmarks, args):
        if args:
            def find(bookmark):
                return all(map(lambda arg: arg in bookmark, args))
            filteredKeys = list(filter(find, bookmarks))
            bookmarks = {x:bookmarks[x] for x in filteredKeys}
        return bookmarks

    def bookmarks(self, args):
        bookmarks = self.filterByArgs(self.m.getBookmarks(), args)
        for name, num in bookmarks.items():
            self.show("{}\t{}\n".format(num, name))

    def bookmark(self, args):
        arg = ' '.join(args)
        if arg:
            self.m.getBookmarks()[arg] = self.current()
            self.bookmarks([])
        else:
            return self.bookmarks()

    def delBookmark(self, args):
        arg = ' '.join(args)
        self.m.delBookmark(arg)
        self.log("Bookmark deleted")

    def getExitData(self, source, to):
        return self.m.getExitData(source, to)

    def addExitData(self, source, target, data):
        try:
            exd = self.m.getExitData(source, target)
        except KeyError:
            self.log("Exit not found")
        exd.update(data)
        self.m.setExitData(source, target, exd)
        return self.here([self.current()])

    def allCoords(self, args):
        for area, startRoom in self.m.getAreas().items():
            self.log("Coordinatifying {} at {}".format(area, startRoom))
            self.draw(200, 200, True, startRoom)

    def draw(self, sizeX=None, sizeY=None, storeCoords=False, at=None):
        # Draw room at x,y,z. Enumerate exits. For each exit target, breadth-first, figure out its new dimensions, rinse, repeat.
        # █▓▒░
        if sizeX and sizeY:
            columns, lines = sizeX, sizeY
        else:
            columns, lines = 60, 100  # shutil.get_terminal_size((21, 22))

        def adjustExit(x, y, z, d, prev):
            m = re.match(r'open .+;(.+)', d)
            if m:
                return adjustExit(x, y, z, m.group(1), prev)
            if d in ['n', 'north']:
                return x, y-1, z, '│', '↑', '║'
            if d in ['w', 'west']:
                return x-1, y, z, '─', '←', '═'
            if d in ['s', 'south']:
                return x, y+1, z, '│', '↓', '║'
            if d in ['e', 'east']:
                return x+1, y, z, '─', '→', '═'
            if d in ['d', 'down']:
                if prev == '▲':
                    return x, y, z-1, '◆', '◆', '◆'
                else:
                    return x, y, z-1, '▼', '▼', '▼'
            if d in ['u', 'up']:
                if prev == '▼':
                    return x, y, z+1, '◆', '◆', '◆'
                else:
                    return x, y, z+1, '▲', '▲', '▲'
            if d in ['nw', 'northwest']:
                return x-1, y-1, '\\', '\\', '\\'
            if d in ['sw', 'southwest']:
                return x-1, y+1, '/', '/', '/'
            if d in ['se', 'southeast']:
                return x+1, y+1, '\\', '\\', '\\'
            if d in ['ne', 'northeast']:
                return x+1, y-1, '/', '/', '/'

        out = []  # NB! indices are out[y][x] because the greater chunks are whole lines
        for _ in range(lines - 1):  # -1 for the next prompt
            out.append([' '] * columns)

        # The only room coordinates that matter are the start room's -- the rest get calculated by tracing paths.
        # startX, startY, startZ = (0, 0, 0)  # self.m.getRoomCoords(self.current())
        centerX, centerY = (columns-1)//2, (lines-1)//2
        data = self.m.getRoomData(at or self.current())
        area = data['zone']

        roomq = collections.deque()
        roomq.append((centerX, centerY, 0, at or self.current()))

        visited = set()

        def getExitLen(source, to):
            exitData = self.getExitData(source, to)
            if not exitData or 'len' not in exitData:
                return 0
            return int(exitData['len'] * 2)

        def fits(x, y, storeCoords):
            doesFit = 0 <= x and x < columns and 0 <= y and y < lines-1
            if not doesFit and storeCoords:
                self.log("Warning, area is bigger than fits into the output. Retry with a larger size lest some rooms remain uncoordinated.")
            return doesFit

        # TODO: one-way exits
        # TODO: draw doors
        coordCache = {}  # Remember where we drew each room, to search for broken-looking exits. Buggy, it still sometimes looks weird on map :(
        while roomq:
            drawX, drawY, drawZ, room = roomq.popleft()
            if room not in visited:  # A given room might end up in the queue through different paths
                # mapX, mapY, mapZ = self.m.getRoomCoords(room)
                if storeCoords:
                    self.m.setRoomCoords(room, drawX // 2, drawY // 2, drawZ // 2)
                visited.add(room)
                # It's possible to keep walking through z layers and end up back on z=initial, which might produce nicer maps -- but we'll have to walk the _whole_ map, or bound by some range.
                out[drawY][drawX] = '█'
                coordCache[room] = (drawX, drawY)
                # out[drawY][drawX] = str(count % 10)
                # count += 1
                exits = self.m.getRoomExits(room)
                for d, tgt in exits.items():
                    tgt = tgt['tgt']
                    if d in ['n', 'e', 's', 'w', 'u', 'd', 'ne', 'se', 'sw', 'nw', 'north', 'east', 'south', 'west', 'up', 'down', 'northeast', 'southeast', 'northwest', 'southwest'] or re.match(r'open .+;[neswud]+', d):
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
                        exZ = drawZ

                        roomX, roomY, roomZ = exX, exY, exZ
                        # Figure out the coordinates of the target room
                        for _ in range(exitLen + 1):  # exitlen for the exit, +1 for the target room
                            roomX, roomY, roomZ, _, _, _ = adjustExit(roomX, roomY, roomZ, d, ' ')

                        exitData = self.m.getExitData(room, d)
                        if 'draw' in exitData and not exitData['draw']:
                            nexX, nexY, nexZ, _, _, _ = adjustExit(exX, exY, exZ, d, out[drawY][drawX])
                            if nexY < len(out) and nexX < len(out[nexY]):
                                out[nexY][nexX] = '.'
                        else:
                            # Mark exits that break map (if the target room is already drawn, but not adjacent to this one)
                            mark = False
                            if tgt in visited:
                                tgtX, tgtY = coordCache[tgt]
                                if tgtX != roomX or tgtY != roomY:
                                    # print("Offset detected:", roomX - tgtX, roomY-tgtX)
                                    mark = True

                            # draw a long exit for beautification
                            for _ in range(exitLen):
                                exX, exY, exZ, regularExit, hiddenExit, markedExit = adjustExit(exX, exY, exZ, d, out[drawY][drawX])
                                if fits(exX, exY, storeCoords):
                                    # If the map grid element we'd occupy is already occupied, don't go there
                                    nextX, nextY, nextZ, _, _, _ = adjustExit(exX, exY, exZ, d, ' ')  # Adjust again, ie. go one step further in the same direction for the target room
                                    # Don't overwrite already drawn areas
                                    free = fits(exX, exY, storeCoords) and (not fits(nextX, nextY, storeCoords) or out[nextY][nextX] == ' ') or tgt in visited

                                    if mark:
                                        out[exY][exX] = markedExit
                                    elif free and exists and sameAreas:
                                        out[exY][exX] = regularExit
                                    else:
                                        out[exY][exX] = hiddenExit

                            visit = (exists
                                    and tgt not in visited
                                    and sameAreas
                                    and (storeCoords or d not in ['u', 'd'])
                                    and fits(roomX, roomY, storeCoords)
                                    and (storeCoords or out[roomY][roomX] == ' ')
                                    )
                            if visit:
                                roomq.append((roomX, roomY, roomZ, tgt))

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
        # self.save([self.mapfname])
        if 'visited' not in self.world.state:
            self.world.state['visited'] = set()
        self.log("Visited {} rooms today!".format(len(self.world.state['visited'])))

    def save(self, args):
        if len(args) == 1:
            self.mapfname = args[0]
        with open(self.mapfname, 'w') as f:
            f.write(self.m.serialize())
        self.log("Serialized map to", self.mapfname)

    def door(self, args):
        if len(args) != 1:
            self.log("Usage: #map door [n/e/s/w/u/d]")
            return
        direction = args[0]
        if direction not in "neswud":
            self.log("Usage: #map door [n/e/s/w/u/d]")
            return

        srcNr = self.current()
        exitsInSrcRoom = self.m.getRoomExits(srcNr)
        exitsInSrcRoom["open {direction}\n{direction}".format(direction=direction)] = exitsInSrcRoom[direction]

        dstNr = exitsInSrcRoom[direction]['tgt']
        exitsInDstRoom = self.m.getRoomExits(dstNr)
        exitsInDstRoom["open {direction}\n{direction}".format(direction=reverse[direction])] = exitsInDstRoom[reverse[direction]]

        self.log(exitsInSrcRoom)
        self.log(exitsInDstRoom)

        self.m.addRoom(
                srcNr,
                self.m.getRoomName(srcNr),
                self.m.getRoomData(srcNr),
                exitsInSrcRoom)

        self.m.addRoom(
                dstNr,
                self.m.getRoomName(dstNr),
                self.m.getRoomData(dstNr),
                exitsInDstRoom)

        self.log("Added custom exit, both ways: open {direction};{direction}".format(direction=direction))

    def startExit(self, args):
        self.exitKw = ' '.join(args)
        nr = roomnr(self.world.gmcp['room']['info']['num'])
        room = self.world.gmcp['room']['info']
        self.exitFrom = {}
        self.exitFrom['exits'] = {}
        self.exitFrom['id'] = nr
        self.exitFrom['name'] = room['name']
        self.exitFrom['data'] = dict(zone=room['zone'], terrain = room['terrain'])
        for k, v in room['exits'].items():
            self.exitFrom['exits'][k.lower()] = {'tgt': roomnr(v)}
        self.log("Type '#map endexit' when you're in the right room, or #map endexit abort")
        self.exitKw = self.exitKw.replace(';', '\n')
        self.exitKw = self.exitKw.replace('~', '\n')
        self.log("Exit: " + repr(self.exitKw))
        self.send(self.exitKw)

    def endExit(self, args):
        if len(args) != 0:
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

    def lockExit(self, args, hard=False):
        direction, level = args if len(args) > 1 else (args[0], -1)
        tgt = self.getRoomByDirection(direction)
        if not tgt:
            self.mud.log("Exit doesn't exist")
            return
        self.addExitData(self.current(), direction, {'hardLock' if hard else 'lock': int(level)})
        return self.here([self.current()])

    def unlockExit(self, args, hard=False):
        direction, level = args if len(args) > 1 else (args[0], -1)
        tgt = self.getRoomByDirection(direction)
        if not tgt:
            self.mud.log("Exit doesn't exist")
            return
        exitData = self.getExitData(self.current(), direction)
        key = 'hardLock' if hard else 'lock'
        if key in exitData:
            del exitData[key]
            self.m.setExitData(self.current(), direction, exitData)
            self.log("Deleted {}".format(key))
        else:
            self.log("{} not found here".format(key))
        return self.here([self.current()])

    def lockExitHard(self, args):
        return self.lockExit(args, hard=True)

    def startRoom(self, args):
        self.m.setAreaStart(self.currentZone(), self.current())

    def noDraw(self, args):
        direction = args[0]
        tgt = self.getRoomByDirection(direction)
        if not tgt:
            self.mud.log("Exit doesn't exist")
            return
        exitData = self.m.getExitData(self.current(), direction)
        draw = 'draw' in exitData and not exitData['draw']
        self.log("Drawing exit {} is now {}".format(direction, draw))
        self.addExitData(self.current(), direction, {'draw': draw})
        return self.here([self.current()])

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

    def findById(self, args, inArea=True):
        res = self.world.state['map-find-result'] = self.m.findRoomsById(' '.join(args), self.currentArea() if inArea else None)
        res.sort(key=lambda x: x[1])
        res.sort(key=lambda x: x[2])
        count = 1
        for nr, name, area in res:
            self.show("{count}\t{nr}\t{name}\t\t{area}\n".format(count=count, nr=nr, name=name, area=area))
            count += 1

    def currentArea(self):
        return self.m.getRoomData(self.current())['zone']

    def unmapped(self, unvisited: bool, inArea: bool, one: bool, bypassLocks: bool):
        if unvisited and 'visited' not in self.world.state:
            self.world.state['visited'] = set()
        here = self.current()
        area1 = self.currentArea()
        unmappedRoom = None
        paths = {here: []}

        def visitExit(room, exDir, tgt):
            nonlocal unmappedRoom
            path = paths[room] + [exDir]
            paths[tgt] = path
            area2 = self.m.getRoomArea(tgt)
            if not area2: # unmapped
                unmappedRoom = tgt
                return True
            if inArea and area1 != area2:
                return True
            if unvisited and tgt not in self.world.state['visited']:
                unmappedRoom = tgt
                return True
            return unmappedRoom

        def visitRoom(room):
            nonlocal unmappedRoom
            return unmappedRoom  # Hack: stop search if we found any unmapped room

        self.m.bfs(here, visitRoom, visitExit, bypassLocks=bypassLocks, enterMazes=True, swim=False)
        return unmappedRoom, paths.get(unmappedRoom)

    def goUnvisited(self, args):
        unvisitedRoomNr, path = self.unmapped(unvisited=True, inArea=True, one=True, bypassLocks=False)
        path = assemble(path, 'go')
        self.log("Visiting {}: {}".format(unvisitedRoomNr, path))
        self.send(path.replace(';', '\n'))

    def autoMap(self, args=None):
        if 'autoMapMode' not in self.world.state:
            self.world.state['autoMapMode'] = 'map'
        if 'autoMapWalk' not in self.world.state:
            self.world.state['autoMapWalk'] = 'go'
        if args:
            for arg in args:
                if arg == 'go=run':
                    self.world.state['autoMapWalk'] = 'run'
                elif arg == 'go=go':
                    self.world.state['autoMapWalk'] = 'go'
                # Bard mode - visit all rooms of this area regardless of mapped status
                elif arg == 'mode=visit':
                    self.world.state['autoMapMode'] = 'visit'
        if args and args[0] == 'stop':
            del self.world.state['autoMapTarget']
            del self.world.state['autoMapSource']
            del self.world.state['autoMapArea']
            del self.world.state['autoMapMode']
            self.log("Stopped autoMap")
            return
        if not args or args[0] != 'exit':
            self.world.state['autoMapArea'] = self.currentArea()
        unmappedRoomNr, path = self.unmapped(unvisited=self.world.state['autoMapMode'] == 'visit', inArea='autoMapArea' in self.world.state, one=True, bypassLocks=self.world.state['autoMapMode'] == 'visit')
        if unmappedRoomNr:
            self.world.state['autoMapTarget'] = unmappedRoomNr
            self.world.state['autoMapSource'] = self.current()
            path = assemble(path, self.world.state['autoMapWalk'])
            self.log("{} to {}: {}".format(self.world.state['autoMapWalk'], unmappedRoomNr, path))
            self.send(path.replace(';', '\n'))
        else:
            self.log("Done! ({})".format(self.world.state.get('autoMapMode')))
            self.autoMap(['stop']) # cleanup

    def areas(self, args):
        areas = self.filterByArgs(self.m.getAreas(), args)
        for name, num in areas.items():
            self.show("{}\t{}\n".format(num, name))

    def delExits(self, args):
        value = self.world.gmcp['room']['info']
        id = roomnr(value['num'])
        data = dict(zone=value['zone'], terrain = value['terrain'])
        name = value['name']
        self.m.addRoom(id, name, data, {})
        return self.here([self.current()])

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

    def areaConnectionsGraph(self, args):
        try:
            self.m.areaConnectionsGraph()
        except:
            import traceback
            self.log(traceback.format_exc())
        else:
            self.log("Done, area connections written to areaconnections.dot - use GraphViz to visualize it: dot -Tsvg areaconnections.dot")

    def nearbyAreas(self, args):
        withPath = args and args[0] == 'path'
        try:
            nearby = self.m.nearbyAreas(self.current(), withPath)
            self.log('\n'.join(map(lambda x: x.replace('\n', '~'), nearby)))
        except Exception as e:
            self.log("Error:")
            import traceback
            self.log(traceback.format_exc())

    def terrains(self, args):
        try:
            area = self.m.getRoomArea(self.current())
            roomsOfCurrentArea = filter(lambda kvp: self.m.getRoomArea(kvp[0]) == area, self.m.m['rooms'].items())
            terrains = {} # terrain to count
            for kvp in roomsOfCurrentArea:
                room = kvp[1]
                terrain = room.get('data', {}).get('terrain')
                if terrain not in terrains:
                    terrains[terrain] = 1
                else:
                    terrains[terrain] += 1
            self.log("Terrains in the current area:\n{}".format(pprint.pformat(terrains)))
        except Exception as e:
            self.log("Error:")
            import traceback
            self.log(traceback.format_exc())

    def __init__(self, mud, drawAreas, mapfname, spacesInRun=True):
        super().__init__(mud)
        self.drawAreas = drawAreas
        self.spacesInRun = spacesInRun
        self.load([mapfname])

        self.commands = {
                'lock': self.lockExit,
                'swim': lambda args: self.addExitData(self.current(), args[0], {'swim': 1}),
                'fly': lambda args: self.addExitData(self.current(), args[0], {'fly': 1}),
                'crawl': lambda args: self.addExitData(self.current(), args[0], {'crawl': 1}),
                'climb': lambda args: self.addExitData(self.current(), args[0], {'climb': 1}),
                'unlock': self.unlockExit,
                'unlock!': lambda args: self.unlockExit(args, hard=True),
                'lock!': lambda args: self.addExitData(self.current(), args[0], {'hardLock': -1}),
                'unmapped': lambda args: self.log('\n' + '\n'.join([str(i) for i in self.unmapped(unvisited=False, inArea=True, one=False, bypassLocks=False)])),
                'unvisited': lambda args: self.log('\n' + '\n'.join([str(i) for i in self.unmapped(unvisited=True, inArea=True, one=False, bypassLocks=False)])),
                # TODO use the path 'gounmapped': lambda args: self.go(self.unmapped(unvisited=False, inArea=True, one=True, bypassLocks=False)[0], 'go'),
                # 'TODO use the path goanyunmapped': lambda args: self.go((self.unmapped(unvisited=False, inArea=True, one=True) or self.unmapped(unvisited=False, inArea=False, one=True, bypassLocks=False))[0], 'go'),
                'gounvisited': self.goUnvisited,
                'av': self.autoMap,
                'areas': self.areas,
                'find': self.find,
                'load': self.load,
                'read': self.load,
                'help': self.help,
                'here': self.here,
                'add': self.bookmark,
                'bookmark': self.bookmark,
                'rm': self.delBookmark,
                'name': self.bookmark,
                'bookmarks': self.bookmarks,
                'ls': self.bookmarks,
                'path': lambda args: self.path(' '.join(args), 'go'),
                'path!': lambda args: self.path(' '.join(args), 'go', bypassLocks=True),
                'go': lambda args: self.go(' '.join(args), 'go'),
                'go!': lambda args: self.go(' '.join(args), 'go', bypassLocks=True),
                'run': lambda args: self.go(' '.join(args), 'run'),
                'run!': lambda args: self.go(' '.join(args), 'run', bypassLocks=True),
                'save': self.save,
                'write': self.save,
                'door': self.door,
                'startexit': self.startExit,
                'endexit': self.endExit,
                'inc': self.inc,
                'dec': self.dec,
                'delexits': self.delExits,
                'delzone': self.delZone,
                'dump': lambda args: self.log(self.m.m),
                'startroom': self.startRoom,
                'nodraw': self.noDraw,
                'draw': lambda args: self.show(self.draw(int(args[0]), int(args[0]))),
                'coords': lambda args: self.show(self.draw(int(args[0]), int(args[0]), storeCoords=True)),
                'allcoords': self.allCoords,
                'areaconnectionsGraph': self.areaConnectionsGraph,
                'nearby': self.nearbyAreas,
                'id': self.findById,
                'id!': lambda args: self.findById(args, inArea=False),
                'terrains': self.terrains,
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

    def drawMapToFile(self):
        with open('map.txt', 'wt') as f:
            f.write(self.draw())

    def handleGmcp(self, cmd: str, value: dict):
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

        # LambdaMOO's Room.Info
        # {
        #   'area': 'Toint Town',
        #   'exits': {'east': 2029, 'north': 442, 'south': 665, 'west': 590},
        #   'name': 'a shaded street',
        #   'num': 662
        # }

        if cmd.lower() == 'room.info':
            num = roomnr(value['num'])
            if 'visited' not in self.world.state:
                self.world.state['visited'] = set()
            self.world.state['visited'].add(num)
            name = value['name']
            zone = value.get('zone') or value['area']
            if value.get('details'):
                self.log("GMCP details: {}".format(value.get('details')))
            self.m.addArea(zone, num)
            id = value.get('id')
            self.mud.logNoMarker(id)
            data = dict(zone=zone, terrain=value.get('terrain'), id=id)
            maze = isMaze(id)
            if maze:
                data['maze'] = True

            # We wish to retain hidden exits (openable / detectable by some chars)
            # and also custom exits.
            # Therefore, by default, don't purge exits.
            # Except, in CoffeeMUD, mazes change layout every now and then, so don't retain those exits.
            exits = self.m.getRoomExits(num)
            coords = self.m.getRoomCoords(num)
            mazeDataBackup = {}
            if maze:
                def rm(n):
                    if n in exits:
                        if 'data' in exits[n]:
                            mazeDataBackup[n] = exits[n]['data']
                        del exits[n]
                rm('n')
                rm('e')
                rm('s')
                rm('w')
                rm('u')
                rm('d')
                rm('ne')
                rm('nw')
                rm('se')
                rm('sw')

            for direction, target in value['exits'].items():
                tgt = roomnr(target)
                dir = direction.lower()
                if dir not in exits:
                    exits[dir] = {}
                exits[dir]['tgt'] = tgt  # sometimes they change, so let's overwrite
                if dir in mazeDataBackup:
                    exits[dir]['data'] = mazeDataBackup[dir]
                if not self.m.roomExists(tgt):  # doesn't exist yet, insert stub for easy pathfinding
                    self.m.addRoom(tgt, None, {}, {})

            if 'exit_kw' in value:  # SneezyMUD
                for direction, door in value['exit_kw'].items():
                    exits['open {door} {direction};{direction}'.format(door=door, direction=direction)] = exits[direction.lower()]

            self.m.addRoom(num, name, data, exits)
            self.m.setRoomCoords(num, coords[0], coords[1], coords[2])

            if 'autoMapTarget' in self.world.state and self.world.state['autoMapTarget'] == num:
                if 'char' in self.world.gmcp and self.world.gmcp['char']['vitals']['moves'] < 60:
                    self.log("Automapping, but near out of moves")
                elif 'autoMapArea' in self.world.state and self.world.state['autoMapArea'] != self.currentArea():
                    self.log("Automapping, but changed areas. Trying to walk back...")
                    self.world.state['autoMapTarget'] = self.world.state['autoMapSource']
                    self.go(self.world.state['autoMapSource'], self.world.state['autoMapWalk'], bypassLocks=self.world.state['autoMapMode'] == 'visit')
                else:
                    self.autoMap(['exit'] if 'autoMapArea' not in self.world.state else None)

            self.drawMapToFile()
