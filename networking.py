'''
10/7/2025
Kristijan Stojanovski

Various networking functions
'''

# LIBRARIES
import socket
import selectors
import types
import threading
from queue import Queue


# SCRIPTS
from helper import getFileContent
import temp as parser

import time

from helper import getFileContent





HOST = "127.0.0.1"
PORT = 65432

MAX_CONNECTION_BACKLOG = int(getFileContent("/proc/sys/net/core/somaxconn"))
DEFAULT_SOCKET_BYTE_AMOUNT = 1024
CLIENT_MESSAGE_FLAG = False
CLIENT_THREAD_FLAG = True

sel = selectors.DefaultSelector()


def accept_wrapper(sock):
    connection, address = sock.accept()
    print("Connection from: " + str(address))

    connection.setblocking(False)
    data = types.SimpleNamespace(addr=address, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(connection, events, data=data)


def service_connection(key, mask):
    sock = key.fileobj
    data = key.data

    if mask & selectors.EVENT_READ:
        message = sock.recv(DEFAULT_SOCKET_BYTE_AMOUNT)
        if message:
            print(f"Echoing message to {data.addr}: {message.decode("utf-8")}")
            sock.send(message)

        else:
            print(f"Closing connection to {data.addr}...")
            sel.unregister(sock)
            sock.close()
            print("Connection closed.")



def runServer(ip:str, port:int)->int:

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.bind((ip, port))

    if(MAX_CONNECTION_BACKLOG):
        sock.listen(MAX_CONNECTION_BACKLOG//3)
    else:
        sock.listen(1)

    print("Listening on %s:%d" % (ip, port))
    sock.setblocking(False)
    sel.register(sock, selectors.EVENT_READ, data=None)

    try:
        while True:
            events = sel.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    accept_wrapper(key.fileobj)
                else:
                    service_connection(key, mask)

    except KeyboardInterrupt:
        print("Caught keyboard interrupt, exiting...")
    finally:
        sel.unregister(sock)
        sel.close()

    sock.close()

    return 0


def clientSend(sock:socket.socket, q:Queue)->int:

    while True:
        queueInput = q.get()

        if(queueInput == None):
            print("Termination signal received...")
            break

        sock.sendall(str(queueInput).encode("utf-8"))

    print("Exiting...")

    return 0

def clientReceive(sock:socket.socket, q:Queue)->int:

    while True:
        print(f"{sock.getpeername()[0]}: {sock.recv(DEFAULT_SOCKET_BYTE_AMOUNT).decode("utf-8")}")

        if(not CLIENT_THREAD_FLAG):
            break

    return 0

def runClient(ip:str, port:int)->int:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect_ex((ip, port))

    messageQueue = Queue()
    recieveQueue = Queue()


    clientSendThread = threading.Thread(target=clientSend, args=(sock, messageQueue), daemon=True)
    clientReceiveTread = threading.Thread(target=clientReceive, args=(sock, recieveQueue), daemon=True)

    clientSendThread.start()
    clientReceiveTread.start()

    try:
        parser.init()
        while True:
            payload = parser.parse_Data()
            stdin = str(payload)

            if(stdin == "exit"):
                messageQueue.put(None)
                print("Termination signal received...")
                break
            if(stdin != ""):
                messageQueue.put(stdin)

            time.sleep(5)
    except KeyboardInterrupt:
        print("\nCaught keyboard interrupt, exiting...")


    sock.close()

    return 0