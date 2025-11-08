import socket
import sys
import time
from threading import Event
import json
import ssl
from enum import IntEnum, auto
from helper import *
import temp

HOST = "homeassistant"
PORT = 1883
CLIENTID = "client-1"
MAX_QOS_PACKET_ATTEMPTS = 10

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


def constructControlHeader(packetType: ControlHeaderType, variableHeaderSize: int, payloadSize: int, flags: int = 0x00) -> bytearray:
    fixedHeader = bytearray()

    fixedHeader += (packetType | flags).to_bytes(1, byteorder='big')

    remainingLength = variableHeaderSize + payloadSize

    fixedHeader += encodeVarint(remainingLength)

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

def constructPayload(self, payload: str | bytes) -> bytearray:
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

    def __receive_packet(self) -> tuple[int, bytes]:

        byte1 = self.__receiveAmountOfBytes(1)[0]
        packetType = byte1 & 0xF0

        remaining = decodeVarint(self.__receiveAmountOfBytes)

        payload = self.__receiveAmountOfBytes(remaining) if remaining else b''

        return packetType, payload

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
        return bytes([ControlHeaderType.PINGREQ, 0x00])

    def __constructPublishPacket(self, topic: str, payloadIn: str, qosLevel: MQTTFlags, qosPacketIdentifier: int | None, duplicate: bool = False) -> bytes:
        '''
        Fixed Header                    Variable Header                 Payload
        PacketType - 4 Bits             Topic Name Length - 2 Bytes     Payload Length - 2 Bytes
        []                              Topic Name                      Data
        Flags - 4 Bits                  Packet Identifier(Qos > 0)
        [Duplicate, Qos, Retain]
        Remaining Length - 1-4 Bytes
        Retain Always True
        Duplicate - Input
        Qos - Input
        '''

        topicBytes = enc_utf8(topic)

        variableHeader = bytearray(topicBytes)

        if qosPacketIdentifier is not None:
            variableHeader += qosPacketIdentifier.to_bytes(2, byteorder='big')


        payload = payloadIn.encode('utf-8')

        controlFlags = 0x00
        controlFlags |= MQTTFlags.RETAIN
        controlFlags |= qosLevel
        if duplicate:
            controlFlags |= MQTTFlags.DUP

        fixedHeader = constructControlHeader(ControlHeaderType.PUBLISH, len(variableHeader), len(payload), controlFlags)

        return fixedHeader + variableHeader + payload

    def __constructPubRelPacket(self) -> bytes:
        return bytes([ControlHeaderType.PUBREL, 0x00])

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

        print("Connect Packet Sent")

        # Confirm The Connection
        connackPacket = self.__receive_packet()

        if connackPacket[0] == ControlHeaderType.CONNACK:
            print("Connack Packet Received")

        self.sock.sendall(self.__constructPingReqPacket())
        type, payload = self.__receive_packet()
        assert type == ControlHeaderType.PINGRESP and payload == b''

        print("CONNACK Packet Received")

    def __disconnect(self):
        self.sock.sendall(self.__constructDisconnectPacket())
        self.sock.close()
        self.sock = None

    def ping(self):
        pass
    def __publish(self, topicLevel: str, topicData: str | dict | int | float | bool, qosLevel: MQTTFlags):
        constructedTopics = {}

        if isinstance(topicData, (str, int, float, bool)):
            constructedTopics[topicLevel] = str(topicData)

        elif isinstance(topicData, dict):
            for key, value in topicData.items():
                constructedTopics[key] = str(value)

        successfulPackets = 0

        for key, value in constructedTopics.items():
            itterations = 1
            packet = self.__constructPublishPacket(key, value, qosLevel, itterations, False)

            match qosLevel:
                case MQTTFlags.QOS1:
                    while True:
                        self.sock.sendall(packet)
                        print(packet)
                        print(packet.hex())

                        inPacket = self.__receive_packet()

                        if inPacket[0] == ControlHeaderType.PUBACK:
                            successfulPackets += 1
                            print(f"PUBACK Packet Received. Successful Packets: {successfulPackets}")
                            break

                        itterations += 1
                        if itterations > MAX_QOS_PACKET_ATTEMPTS:
                            print(f"Max QoS1 Send Attempts Reached.\nPacket: {packet}")
                            break

                        packet = self.__constructPublishPacket(key, value, qosLevel, itterations, True)

                case MQTTFlags.QOS2:
                    while True:
                        self.sock.sendall(packet)
                        inPacket = self.__receive_packet()

                        if inPacket[0] == ControlHeaderType.PUBREC:
                            self.sock.sendall(self.__constructPubRelPacket())
                            inPacket == self.__receive_packet()
                            if inPacket[0] == ControlHeaderType.PUBCOMP:
                                successfulPackets += 1
                                break

                        itterations += 1
                        if itterations > MAX_QOS_PACKET_ATTEMPTS:
                            print(f"Max QoS1 Send Attempts Reached.\nPacket: {packet}")
                            break

                        packet = self.__constructPublishPacket(key, value, qosLevel, itterations, False)

    def run(self):
        print("Starting MQTT Client")
        try:
            self.__connect()
        except Exception as e:
            print(f"Failed to connect to MQTT server at {self.host}:{self.port}. Error: {e}")
            quit()
        print("connection succeeded")

        temp.init()
        sensorData = temp.parse_Data()

        dataFlag = True

        for value in sensorData.values():
            if isinstance(value, (str, None)):
                dataFlag = False

        bme680topic = "homeassistant/sensor/bme680/state"

        dummy_sensor_data = {
            "Temperature": 24.6,
            "Humidity": 41.3,
            "Pressure": 1012.8,
            "Gas": 12000
        }

        bme680config = {
            "homeassistant/sensor/bme680_temperature/config": {
                "name": "BME680 Temperature", "unique_id": "bme680_temperature",
                "state_topic": "homeassistant/sensor/bme680/state",
                "device_class": "temperature", "unit_of_measurement": "°C",
                "value_template": "{{ value_json.Temperature }}",
                "device": {"identifiers": ["bme680_bridge"], "name": "BME680 Bridge"},
                "availability_topic": "homeassistant/sensor/bme680/availability"
            },
            "homeassistant/sensor/bme680_humidity/config": {
                "name": "BME680 Humidity", "unique_id": "bme680_humidity",
                "state_topic": "homeassistant/sensor/bme680/state",
                "device_class": "humidity", "unit_of_measurement": "%",
                "value_template": "{{ value_json.Humidity }}",
                "device": {"identifiers": ["bme680_bridge"]},
                "availability_topic": "homeassistant/sensor/bme680/availability"
            },
            "homeassistant/sensor/bme680_pressure/config": {
                "name": "BME680 Pressure", "unique_id": "bme680_pressure",
                "state_topic": "homeassistant/sensor/bme680/state",
                "device_class": "pressure", "unit_of_measurement": "hPa",
                "value_template": "{{ value_json.Pressure }}",
                "device": {"identifiers": ["bme680_bridge"]},
                "availability_topic": "homeassistant/sensor/bme680/availability"
            },
            "homeassistant/sensor/bme680_gas/config": {
                "name": "BME680 Gas", "unique_id": "bme680_gas",
                "state_topic": "homeassistant/sensor/bme680/state",
                "unit_of_measurement": "Ω",
                "value_template": "{{ value_json.Gas }}",
                "device": {"identifiers": ["bme680_bridge"]},
                "availability_topic": "homeassistant/sensor/bme680/availability"
            }
        }

        if dataFlag:
            payload = json.dumps(sensorData)
        else:
            payload = json.dumps(dummy_sensor_data)

        for topic, config in bme680config.items():
            self.__publish(topic, json.dumps(config), MQTTFlags.QOS1)

        self.__publish("homeassistant/sensor/bme680/availability", "online", MQTTFlags.QOS1)
        self.__publish("homeassistant/sensor/bme680/state", payload, MQTTFlags.QOS1)


        for i in range(20, 0, -1):
            print(f"Stopping in {i}...")
            time.sleep(1)

        self.__disconnect()





client = MQTTSocketClient(CLIENTID, username="oniic", password="Saltersimp5904", host=HOST, port=PORT)
client.run()