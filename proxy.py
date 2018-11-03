#!/usr/bin/env python3

import queue
import random
import socket
import socketserver
import threading
import time

TGT_HOST = 'localhost'
TGT_PORT = 4000
LISTEN_HOST = '::1'
LISTEN_PORT = 1234

eof = object()
# to server
client_to_mud_q = queue.Queue()
# from server
mud_to_client_q = queue.Queue()
mudside_connected = False
client_sessions = []


class MyTCPServer(socketserver.ThreadingTCPServer):
    address_family = socket.AF_INET6
    allow_reuse_address = True


def log(arg):
    print("{} {}".format(threading.get_ident(), arg))


class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    request_queue_size = 1
    address_family = socket.AF_INET6

    def my_send(self, shutdown1):
        log("Starting my_send")
        while not shutdown1.is_set():
            data = mud_to_client_q.get(block=True)
            self.request.sendall(data)
        shutdown1.clear()
        log("Ending my_send")

    def my_receive(self, shutdown2):
        log("starting my_receive")
        while not shutdown2.is_set():
            data = self.request.recv(1024)
            if not data:
                break
            # print("{} wrote {} bytes".format(self.client_address[0], len(data)))
            # print(data)
            client_to_mud_q.put(data)
        shutdown2.clear()
        log("Ending my_receive")

    def handle(self):
        print("Incoming client connection")

        for event in client_sessions:
            print("Kicking out old client")
            event.set()
        del client_sessions[:]
        
        shutdown1 = threading.Event()
        shutdown2 = threading.Event()
        client_sessions.append(shutdown1)
        client_sessions.append(shutdown2)

        self.send_thr = threading.Thread(target=self.my_send, args=[shutdown1])
        self.recv_thr = threading.Thread(target=self.my_receive, args=[shutdown2])
        self.send_thr.start()
        self.recv_thr.start()
        self.send_thr.join()
        self.recv_thr.join()
        print("Incoming client connection closed")

    def setup(self):
        pass


# MUD client, talking to server
def mud_to_client_threadfn(mud_sock):
    print("mud_to_client_threadfn started")
    while True:
        data = mud_sock.recv(1024)
        if not data:
            break
        # print("Got data from server, %d bytes" % len(data))
        mud_to_client_q.put(data)
    global mudside_connected
    mudside_connected = False
    client_to_mud_q.put(eof)
    print("mud_to_client_threadfn ended")


def client_to_mud_threadfn(mud_sock):
    print("client_to_mud_threadfn started")
    while True:
        data = client_to_mud_q.get(block=True)
        if data is eof:
            break
        else:
            mud_sock.sendall(data)
    print("client_to_mud_threadfn ended")


def keepalive():
    global mudside_connected
    while True:
        if mudside_connected:
            print("*keepalive*")
            client_to_mud_q.put(b"\r")
        time.sleep(random.randint(101,299))


if __name__ == "__main__":
    connected_thr = threading.Thread(target=keepalive)
    connected_thr.start()
    print("Starting listener on %s:%d" % (LISTEN_HOST, LISTEN_PORT))
    server = MyTCPServer((LISTEN_HOST, LISTEN_PORT), MyTCPHandler)


    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    ser_thr = threading.Thread(target=server.serve_forever)
    ser_thr.start()

    # while True:
    print("Starting mudside connection to %s:%d" % (TGT_HOST, TGT_PORT))
    mud_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        mud_sock.connect((TGT_HOST, TGT_PORT))
        mudside_connected = True
    except:
        pass
    else:
        print("Outgoing mudside_connected")
        cli_recv_thr = threading.Thread(target=mud_to_client_threadfn, args=[mud_sock])
        cli_send_thr = threading.Thread(target=client_to_mud_threadfn, args=[mud_sock])
        cli_recv_thr.start()
        cli_send_thr.start()
        cli_recv_thr.join()
        cli_send_thr.join()
    # time.sleep(1)

    ser_thr.join()
