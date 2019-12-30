#!/usr/bin/env python3

from proxy import proxy
from select import select
import importlib
import json
import os
import pprint
import re
import sys
import telnetlib
import threading
import traceback
telnetlib.GMCP = b'\xc9'


class Session(object):
    def __init__(self, world_module, port, arg):
        self.mud_encoding = 'iso-8859-1'
        self.client_encoding = 'utf-8'
        self.gmcp = {}
        self.world_module = world_module
        self.arg = arg
        self.world = world_module.getClass()(self, self.arg)
        try:
            self.socketToPipeR, self.pipeToSocketW, self.stopFlag, runProxy = proxy('::1', port)
            self.pipeToSocketW = os.fdopen(self.pipeToSocketW, 'wb')
            self.proxyThread = threading.Thread(target=runProxy)
            self.proxyThread.start()
            host_port = self.world.getHostPort()
            self.log("Connecting")
            self.telnet = self.connect(*host_port)
            self.log("Connected")
        except:
            self.log("Shutting down")
            self.stopFlag.set()
            self.world.quit()
            raise

    def join(self):
        self.thr.join()

    def log(self, *args, **kwargs):
        if len(args) == 1 and type(args[0]) == str:
            line = args[0]
        else:
            line = pprint.pformat(args)
        self.pipeToSocketW.write("---------\n".encode(self.client_encoding))
        self.pipeToSocketW.write(line.encode(self.client_encoding))
        self.pipeToSocketW.write(b"\n")
        self.pipeToSocketW.flush()

    def strip_ansi(self, line):
        return re.sub(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]', '', line)

    def gmcpOut(self, msg):
        self.telnet.sock.sendall(telnetlib.IAC + telnetlib.SB + telnetlib.GMCP + msg.encode(self.mud_encoding) + telnetlib.IAC + telnetlib.SE)

    def iac(self, sock, cmd, option):
        if cmd == telnetlib.WILL:
            if option == telnetlib.GMCP:
                self.log("Enabling GMCP")
                sock.sendall(telnetlib.IAC + telnetlib.DO + option)
                self.gmcpOut('Core.Hello { "client": "Cizra", "version": "1" }')
                supportables = ['char 1', 'char.base 1', 'char.maxstats 1', 'char.status 1', 'char.statusvars 1', 'char.vitals 1', 'char.worth 1', 'comm 1', 'comm.tick 1', 'group 1', 'room 1', 'room.info 1']
                self.gmcpOut('Core.Supports.Set ' + str(supportables).replace("'", '"'))
                self.gmcpOut('request room')
                self.gmcpOut('request char')
            elif option == telnetlib.TTYPE:
                self.log("Sending terminal type 'Cizra'")
                sock.sendall(telnetlib.IAC + telnetlib.DO + option +
                        telnetlib.IAC + telnetlib.SB + telnetlib.TTYPE + telnetlib.BINARY + b'Cizra' + telnetlib.IAC + telnetlib.SE)

            else:
                sock.sendall(telnetlib.IAC + telnetlib.DONT + option)
        elif cmd == telnetlib.SE:
            data = self.telnet.read_sb_data()
            if data and data[0] == ord(telnetlib.GMCP):
                try:
                    self.handleGmcp(data[1:].decode(self.mud_encoding))
                except Exception as e:
                    traceback.print_exc()

    def handleGmcp(self, data):
        # this.that {JSON blob}
        # TODO: move into clients
        space_idx = data.find(' ')
        whole_key = data[:space_idx]
        value_json = data[space_idx + 1:]
        nesting = whole_key.split('.')
        current = self.world.gmcp
        for nest in nesting[:-1]:
            if nest not in current:
                current[nest] = {}
            current = current[nest]
        lastkey = nesting[-1]
        try:
            val = json.loads(value_json)
        except json.decoder.JSONDecodeError:
            val = {"string": value_json}
        if lastkey not in current:
            current[lastkey] = {}
        current[lastkey] = val
        self.world.handleGmcp(whole_key, val)

    def connect(self, host, port):
        t = telnetlib.Telnet()
        t.set_option_negotiation_callback(self.iac)
        # t.set_debuglevel(1)
        t.open(host, int(port))
        return t

    def send(self, line):
        print("> ", line)
        self.telnet.write((line + '\n').encode(self.mud_encoding))

    def handle_from_telnet(self):
        try:
            data = self.telnet.read_very_eager()
        except:
            self.log("EOF on telnet")
            self.stopFlag.set()
            self.world.quit()
            raise
        try:
            data = data.decode(self.mud_encoding)
        except UnicodeError as e:
            print("Unicode error:", e)
            print("Data was:", data)
            data = ''

        if not data:
            _ = self.telnet.read_sb_data()
        prn = []
        for line in data.split('\n'):
            if line:
                replacement = None
                try:
                    replacement = self.world.trigger(line.strip())
                except Exception as e:
                    traceback.print_exc()
                if replacement is not None:
                    line = replacement
            prn.append(line)
        self.pipeToSocketW.write('\n'.join(prn).encode(self.mud_encoding))
        self.pipeToSocketW.flush()


    def show(self, line):
        self.pipeToSocketW.write(line.encode(self.client_encoding))
        self.pipeToSocketW.flush()


    def handle_from_pipe(self):
        data = b''  # to handle partial lines
        try:
            data += os.read(self.socketToPipeR, 4096)
            lines = data.split(b'\n')
            if lines[-1] != '':  # received partial line, don't process
                data = lines[-1]
            else:
                data = b''
            lines = lines[:-1]  # chop off either the last empty line, or the partial line

            for line in lines:
                line = line.decode(self.client_encoding)
                if line[-1] == '\r':
                    line = line[:-1]
                self.handle_output_line(line)
        except EOFError:
            self.log("EOF in pipe")
            self.stopFlag.set()
            self.world.quit()
            raise


    def handle_output_line(self, data):
        pprint.pprint(data)
        if data == '#reload' and self.world:
            self.log('Reloading world')
            try:
                state = self.world.state
                gmcp = self.world.gmcp
                self.world.quit()
                self.world_module = importlib.reload(self.world_module)
                self.world = self.world_module.getClass()(self, self.arg)
                self.world.state = state
                self.world.gmcp = gmcp
            except Exception:
                traceback.print_exc()
            return
        else:
            handled = False
            try:
                handled = self.world.alias(data)
            except Exception as e:
                traceback.print_exc()
            else:
                if not handled:
                    self.send(data)


    def run(self):
        try:
            while True:
                fds, _, _ = select([self.telnet.get_socket(), self.socketToPipeR], [], [])
                for fd in fds:
                    if fd == self.telnet.get_socket():
                        self.handle_from_telnet()
                    elif fd == self.socketToPipeR:
                        self.handle_from_pipe()
        except Exception as e:
            self.log("Exception in run():", e)
        finally:
            self.log("Closing")
            self.telnet.close()


def main():
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("Usage: {} worldmodule (without .py) port [arg]".format(sys.argv[0]))
        exit(1)

    world_module = importlib.import_module(sys.argv[1])
    port = int(sys.argv[2])
    arg = sys.argv[3] if len(sys.argv) == 4 else None
    ses = Session(world_module, port, arg)
    ses.run()


assert(__name__ == '__main__')
main()
