import queue
import random
import socket
import socketserver
import threading
import time

TGT_HOST = '127.0.0.1'
TGT_PORT = 4010
LISTEN_HOST = '::1'
LISTEN_PORT = 4000

eof = object()
# to server
to_q = queue.Queue()
# from server
from_q = queue.Queue()
global connected
connected = False


class MyTCPServer(socketserver.TCPServer):
    address_family = socket.AF_INET6
    allow_reuse_address = True


class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    request_queue_size = 1
    address_family = socket.AF_INET6

    def my_send(self):
        print("Starting my_send")
        while True:
            data = from_q.get(block=True)
            if data is eof:
                break
            else:
                self.request.sendall(data)
        print("Ending my_send")

    def my_receive(self):
        print("starting my_receive")
        while True:
            data = self.request.recv(1024)
            if not data:
                break
            print("{} wrote {} bytes".format(self.client_address[0], len(data)))
            print(data)
            to_q.put(data)
        from_q.put(eof)
        print("Ending my_receive")

    def handle(self):
        print("Incoming client connection")
        self.send_thr = threading.Thread(target=self.my_send)
        self.recv_thr = threading.Thread(target=self.my_receive)
        self.send_thr.start()
        self.recv_thr.start()
        self.send_thr.join()
        self.recv_thr.join()
        print("Incoming client connection closed")

    def setup(self):
        pass


# MUD client, talking to server
def cli_recv(sock):
    print("cli_recv started")
    while True:
        data = sock.recv(1024)
        if not data:
            break
        print("Got data from server, %d bytes" % len(data))
        from_q.put(data)
    global connected
    connected = False
    to_q.put(eof)
    print("cli_recv ended")


def cli_send(sock):
    print("cli_send started")
    while True:
        data = to_q.get(block=True)
        if data is eof:
            break
        else:
            sock.sendall(data)
    print("cli_send ended")


def keepalive():
    global connected
    while True:
        if connected:
            print("*keepalive*")
            to_q.put(b"\r")
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

    while True:
        print("Started outgoing connection to %s:%d" % (TGT_HOST, TGT_PORT))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((TGT_HOST, TGT_PORT))
            connected = True
        except:
            pass
        else:
            print("Outgoing connected")
            cli_recv_thr = threading.Thread(target=cli_recv, args=[sock])
            cli_send_thr = threading.Thread(target=cli_send, args=[sock])
            cli_recv_thr.start()
            cli_send_thr.start()
            cli_recv_thr.join()
            cli_send_thr.join()
        time.sleep(1)

    ser_thr.join()
