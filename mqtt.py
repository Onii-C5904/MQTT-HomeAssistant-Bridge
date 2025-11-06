import socket
import sys
import time
import struct
from threading import Event
import json
import ssl
from enum import IntEnum, auto

HOST = "192.168.122.228"
PORT = 1883
CLIENTID = "client-1"

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

# CONNECT flags bitfield (MQTT v3.1.1)
class MQTTConnectFlags(IntEnum):
    RESERVED       = 0x01            # must be 0
    CLEAN_SESSION  = 0x02            # bit 1
    WILL_FLAG      = 0x04            # bit 2
    WILL_RETAIN    = 0x20            # bit 5
    PASSWORD       = 0x40            # bit 6
    USERNAME       = 0x80            # bit 7

class HeaderType(IntEnum):
    CONNECT = 0

class MQTTWillQoS(IntEnum):
    QOS0    = (0 & 0x03) << 3   # Little hack to push the numbers in to bits 3 and 4
    QOS1    = (1 & 0x03) << 3
    QOS2    = (2 & 0x03) << 3



class MQTTProtocolLevel(IntEnum):
    V3_1_1 = 0x04


def bitwiseOrForBytes(byte1: bytes, byte2: bytes) -> bytes:
    result = bytearray(len(byte1))

    for i in range(len(byte1)):
        result[i] = byte1[i] | byte2[i]

    return bytes(result)

def bitwiseAndForBytes(byte1: bytes, byte2: bytes) -> bytes:
    result = bytearray(len(byte1))

    for i in range(len(byte1)):
        result[i] = byte1[i] & byte2[i]

    return bytes(result)

def enc_utf8(s: str) -> bytes:
    b = s.encode("utf-8")
    return struct.pack("!H", len(b)) + b

def enc_varint(n: int) -> bytes:
    out = bytearray()
    while True:
        digit = n % 128
        n //= 128
        if n > 0:
            digit |= 0x80
        out.append(digit)
        if n == 0:
            break
    return bytes(out)

def dec_varint(recv_fn) -> int:
    multiplier = 1
    value = 0
    while True:
        b = recv_fn(1)
        if not b:
            raise ConnectionError("socket closed decoding varint")
        byte = b[0]
        value += (byte & 0x7F) * multiplier
        if (byte & 0x80) == 0:
            break
        multiplier *= 128
        if multiplier > 128**4:
            raise ValueError("Malformed Remaining Length")
    return value

def constructControlHeader(packetType: ControlHeaderType, variableHeaderSize: int, payloadSize: int) -> bytearray:
    fixedHeader = bytearray()

    fixedHeader += packetType.to_bytes()

    remainingLength = variableHeaderSize + payloadSize

    fixedHeader += enc_varint(remainingLength)

    return fixedHeader

def constructVariableHeader(headerFlags: bytes) -> bytearray:

    '''
    Protocol Name Length 2x bytes
    Protocol Name
    Protocol Level i.e. version
    Content Flag 1x bytes
    Keep Alive
    '''

    variableHeader = bytearray()

    # Variable Header Boiler Plate

    protocolName = b"MQTT"

    variableHeader += len(protocolName).to_bytes(2, byteorder='big')
    variableHeader += protocolName
    variableHeader += MQTTProtocolLevel.V3_1_1.to_bytes(1, byteorder='big')
    variableHeader += headerFlags

    return variableHeader

def constructPayload(self) -> bytearray:
    pass


class MQTTSocketClient:
    def __init__(self, clientID: str, username: str = None, password: str = None, host: str = "homeassistant", port: int = 1883, tls=False, keepalive=60, timeout=10):
        self.clientID = clientID
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.tls = tls
        self.keepalive = keepalive
        self.timeout = timeout
        self.sock: socket.socket | None = None
        self.last_receive = time.time()
        self.last_send = time.time()
        self.connectionTime = None
        self.packet_id = 1

    def __handle_tls(self):
        tlsHandler = ssl.create_default_context()
        return tlsHandler.wrap_socket(self.sock, server_hostname=self.host)

    def __receiveAmountOfBytes(self, n: int) -> bytes:
        packetChunks = []
        receivedBytes = 0

        while receivedBytes < n:
            packetChunk = self.sock.recv(n - receivedBytes)
            if not packetChunk:
                raise ConnectionError("Connection closed during receiving.")
            packetChunks.append(packetChunk)
            receivedBytes += len(packetChunk)

        self.last_receive = time.time()

        return b''.join(packetChunks)

    def __receive_packet(self) -> tuple[IntEnum, bytes]:

        byte1 = self.__receiveAmountOfBytes(1)[0]

        print(byte1)

        if int(byte1) == ControlHeaderType.CONNACK:
            return ControlHeaderType.CONNACK, int(0).to_bytes()

    def __constructConnectPacket(self,  client_id: str, keepalive: int, username: str | None, password: str | None, will_topic: bytes | None, will_payload: bytes | None, will_retain: bool = True, clean_start: bool = True, will_qos: MQTTWillQoS = MQTTWillQoS.QOS1) -> bytes:

        # Construct CONNECT Packet Variable Header flags
        variableFlags = b'\x00'

        if clean_start:
            variableFlags = bitwiseOrForBytes(variableFlags, MQTTConnectFlags.CLEAN_SESSION.to_bytes()) # cause supporting bitwise operations would make too much sense

        if username is not None:
            variableFlags = bitwiseOrForBytes(variableFlags, MQTTConnectFlags.USERNAME.to_bytes())

        if password is not None:
            variableFlags = bitwiseOrForBytes(variableFlags, MQTTConnectFlags.PASSWORD.to_bytes())


        willExists = (will_topic is not None) and (will_payload is not None)
        '''

        if willExists:
            pass
            #variableFlags = bitwiseOrForBytes(variableFlags, MQTTConnectFlags.WILL_FLAG.to_bytes())
            #variableFlags = bitwiseOrForBytes(variableFlags, will_qos.to_bytes())

            if will_retain:
                pass
                #variableFlags = bitwiseOrForBytes(variableFlags, MQTTConnectFlags.WILL_RETAIN.to_bytes())
        '''


        variableHeader = constructVariableHeader(variableFlags)

        # Add the keep alive timer
        variableHeader += struct.pack("!H", keepalive)


        # Construct Payload
        payload = bytearray()
        payload += len(client_id.encode("utf-8")).to_bytes(2, byteorder='big')
        payload += client_id.encode("utf-8")

        '''

        if willExists:
            payload += will_topic
            payload += will_payload
        '''

        if username is not None:
            payload += len(username.encode("utf-8")).to_bytes(2, byteorder='big')
            payload += username.encode("utf-8")

        if password is not None:
            payload += len(password.encode("utf-8")).to_bytes(2, byteorder='big')
            payload += password.encode("utf-8")


        # Construct Fixed Header
        fixedHeader = constructControlHeader(ControlHeaderType.CONNECT, len(variableHeader), len(payload))

        print(f"Fixed Header: {fixedHeader}")
        print(f"Fixed Header Hex: {fixedHeader.hex()}")
        print(f"Variable Header: {variableHeader}")
        print(f"Variable Header Hex: {variableHeader.hex()}")
        print(f"Payload: {payload}")
        print(f"Payload Hex: {payload.hex()}")


        return fixedHeader + variableHeader + payload

    def __constructDisconnectPacket(self) -> bytes:
        return bytes([ControlHeaderType.DISCONNECT, 0])

    def __constructPingReqPacket(self) -> bytes:
        return bytes([ControlHeaderType.PINGREQ, 0])

    def __connect(self):

        self.sock = socket.create_connection((self.host, self.port), self.timeout)

        if self.tls:
            self.sock = self.__handle_tls()

        self.sock.settimeout(self.timeout)

        connectPacket = self.__constructConnectPacket(self.clientID, self.keepalive, self.username, self.password, b"home/bme680/status", b"offline")

        print(connectPacket)
        print(f"Connect Packet Hex: {connectPacket.hex()}")

        self.sock.sendall(connectPacket)
        self.last_send = time.time()
        self.connectionTime = self.last_send

        print("Packet Sent")

        # Confirm The Connection
        while True:
            packetType = self.__receive_packet()[0] # The first index is the packet type, for a connack there is no payload, only thing we care about is that it is a connack


        if packetType != ControlHeaderType.CONNACK.to_bytes(1, byteorder='big'):
            print("Connected But No CONNACK Packet Received")
            raise socket.error

        print("CONNACK Packet Received")


    def __disconnect(self):
        self.sock.sendall(self.__constructDisconnectPacket())
        self.sock.close()
        self.sock = None

    def ping(self):
        pass
    def publish(self):
        pass
    def subscribe(self):
        pass

    def run(self):
        print("Starting MQTT Client")
        try:
            self.__connect()
        except Exception as e:
            print(f"Failed to connect to MQTT server at {self.host}:{self.port}. Error: {e}")
            quit()

        print("connection succeeded")

        self.__disconnect()





client = MQTTSocketClient(CLIENTID, username="oniic", password="Saltersimp5904", host=HOST, port=PORT)
client.run()