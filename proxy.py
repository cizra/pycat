#!/usr/bin/env python3

import queue
import os
import socket
import sys
import threading

from select import select


# returns anonymous pipes (readableFromClient, writableToClient)
def proxy(bindAddr, listenPort):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((bindAddr, listenPort))
    sock.listen(5)
    socketToPipeR, socketToPipeW = os.pipe()
    pipeToSocketR, pipeToSocketW = os.pipe()
    stop = threading.Event()

    return socketToPipeR, pipeToSocketW, stop, lambda: serve(socketToPipeW, pipeToSocketR, sock, stop)


def serve(socketToPipeW, pipeToSocketR, sock, stop):
    socketToPipeW = os.fdopen(socketToPipeW, 'wb')

    clientSocket = None
    clientSockets = []
    addr = None

    pipeToSocketBuffer = []

    while not stop.is_set():
        fds, _, _ = select([sock, pipeToSocketR] + clientSockets, [], [])
        for fd in fds:
            if fd == sock:
                print("new client")
                if clientSocket:
                    print("booting old client")
                    clientSocket.sendall(b"Superseded. Bye!")
                    clientSocket.close()
                clientSocket, addr = sock.accept()
                clientSockets = [clientSocket]
                for item in pipeToSocketBuffer:
                    clientSocket.sendall(item)
                pipeToSocketBuffer = []
            elif fd == clientSocket:
                data = fd.recv(4096)
                if not data:  # disconnect
                    clientSocket.close()
                    clientSocket = None
                    clientSockets = []
                    print("socket disconnected")
                else:
                    socketToPipeW.write(data)  # TODO: partial writes?
                    socketToPipeW.flush()
            elif fd == pipeToSocketR:
                data = os.read(pipeToSocketR, 4096)
                if not data:
                    print("EOF from pipe")
                    break
                if clientSocket:
                    clientSocket.sendall(data)  # TODO: partial writes?
                else:
                    pipeToSocketBuffer.append(data)
    print("Gracefully shutting down in serve")


if __name__ == "__main__":
    def echo(socketToPipeR, pipeToSocketW, stopFlag):
        pipeToSocketW = os.fdopen(pipeToSocketW, 'wb')
        try:
            while not stopFlag.is_set():
                data = os.read(socketToPipeR, 4096)
                print(b"Got %d, sleeping" % (len(data)))
                import time
                time.sleep(1)
                print(b"Echoing %d" % (len(data)))
                pipeToSocketW.write(data)
                pipeToSocketW.flush()
        except KeyboardInterrupt:
            stopFlag.set()
        print("Gracefully shutting down in echo")

    socketToPipeR, pipeToSocketW, stopFlag, work = proxy('::1', 1234)
    echoThr = threading.Thread(target=echo, args=[socketToPipeR, pipeToSocketW, stopFlag])
    echoThr.start()
    try:
        work()
    except KeyboardInterrupt:
        stopFlag.set()
    echoThr.join()
