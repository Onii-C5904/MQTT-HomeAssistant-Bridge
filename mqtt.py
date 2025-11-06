import socket
import time
import struct
from threading import Event
import json
from enum import IntEnum, auto

STOP = Event()

class ControlHeaderType(IntEnum):
    CONNECT     = 0x10  # Client → Server
    CONNACK     = 0x20  # Server → Client
    PUBLISH     = 0x30  # Client or Server
    PUBACK      = 0x40
    PUBREC      = 0x50
    PUBREL      = 0x60
    PUBCOMP     = 0x70
    SUBSCRIBE   = 0x80
    SUBACK      = 0x90
    UNSUBSCRIBE = 0xA0
    UNSUBACK    = 0xB0
    PINGREQ     = 0xC0
    PINGRESP    = 0xD0
    DISCONNECT  = 0xE0

class MQTTFlags(IntEnum):
    RETAIN          = 0x01  # RETAIN = 1 (for PUBLISH)
    QOS1            = 0x02  # QoS level 1
    QOS2            = 0x04  # QoS level 2
    DUP             = 0x08  # DUP flag
    SUBSCRIBE_FLAG  = 0x02  # SUBSCRIBE requires QoS1 (0b0010)

class MQTTProtocolLevel(IntEnum):
    V3_1_1 = 0x04


    def constructControlHeader(self, packetType: ControlHeaderType, flags: MQTTFlags, variableHeaderSize: int, payloadSize: int) -> bytes:
        pass

    def constructVariableHeader(self) -> bytes:
        pass

    def constructPayload(self) -> bytes:
        pass


class MQTTSocketClient:
    def __init__(self, host, port, tls=True, keepalive=60, timeout=10):
        self.host = host
        self.port = port
        self.tls = tls
        self.keepalive = keepalive
        self.timeout = timeout
        self.sock: socket.socket | None = None
        self.last_rx = time.time()
        self.last_tx = time.time()
        self.packet_id = 1

    def connect(self):
        pass

    def disconnect(self):
        pass
    def ping(self):
        pass
    def publish(self):
        pass
    def subscribe(self):
        pass
