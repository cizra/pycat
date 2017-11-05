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


httpheader = """
<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cizrian pathificator</title>
<link rel="stylesheet" href="style.css">
<script src="pathificator.js"></script>
</head>
"""

httpfooter = '</body></html>'

def frontpage():
    body = """
<p>Room names are Case Sensitive!</p>
<form method="POST">
From: <input type="text" name="from" id="inputfrom" oninput="findRoom('from')"><br/>
To: <input type="text" name="to" id="inputto" oninput="findRoom('to')"><br/>
</form>
<p id="path"></p>
<p id="lag"></p>
<table id="roomlist"></table>
"""
    yield httpheader + body + httpfooter


def findRoom(roomName):
    if len(roomName) >= 3:
        return [json.dumps(m.findRoomByName(roomName))]
    else:
        return ["{}"]


def pathFind(args):
    here, there = int(args[0]), int(args[1])
    return [assemble(m.findPath(here, there))]


def route(env, start_response):
    path = env['REQUEST_URI']
    if path == '/':
        yield from frontpage()
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
