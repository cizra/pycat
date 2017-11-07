import mapper.libmapper
from modules.mapper import assemble

import collections
import json
import urllib.parse


m = None
def load():
    with open('sneezy.map', 'r') as f:
        ser = f.read()
    global m
    m = mapper.libmapper.Map(ser)
    print("Loaded map")
load()


def findRoom(roomName):
    if len(roomName) >= 3:
        return [json.dumps(m.findRoomByName(roomName))]
    else:
        return ["{}"]


def pathFind(args):
    here, there = int(args[0]), int(args[1])
    ret = assemble(m.findPath(here, there)) or "Not found :("
    return [ret]


def route(env, start_response):
    path = env['REQUEST_URI']
    if path == '/':
        start_response('302 Found', [('Location', '/connectificator.html')])
    elif path.startswith('/findRoom/'):
        yield from findRoom(urllib.parse.unquote(path.split('/findRoom/')[1]))
    elif path.startswith('/pathFind/'):
        yield from pathFind(path.split('/')[2:])
    elif path == '/crash':
        raise RuntimeError("test crash")
    else:
        start_response('404 Not Found', [('Content-Type', 'text/html')])
        yield "<html><body><h1>404 Errror!</h1><p>Errroooooor! Eeeaaaeeaeeeerrrr...</p>"


def application(env, start_response):
    try:
        start_response('200 OK', [('Content-Type', 'text/html')])# , ('Transfer-Encoding', 'chunked')])
        for line in route(env, start_response):
            if line[-1] != '\n':
                line += '\n'
            yield line.encode('utf-8')
    except Exception:
        # Only protects from exceptions that happen before the first yield.
        start_response('500 Internal Server Error', [('Content-Type', 'text/html')])
        yield "Oops"
        raise
