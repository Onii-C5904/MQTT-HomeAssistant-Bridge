"""
@mainpage Python MQTT–Home Assistant Bridge

This project is a Python-based MQTT bridge for Home Assistant.

It:
- Connects to an MQTT broker
- Publishes sensor data or state changes
- Follows Home Assistant’s MQTT discovery conventions
- Provides a simple, scriptable way to expose devices to Home Assistant
"""

import socket
import time
from threading import Event
import json
import ssl
from enum import IntEnum
from helper import *
import temp
from iio import Device, find_iio_devices

## Constants
USERNAME = ""
PASSWORD = ""
HOST = "homeassistant.local"
PORT = 1883
CLIENTID = "client-1"
MAX_QOS_PACKET_ATTEMPTS = 10000

STOP = Event()

## Control Header Type Enum.
# This enum contains the different packet identification flags for the MQTT Protocol.
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

## MQTT Packet Flags Enum.
# This enum contains the various flags that can be added to a MQTT packet.
class MQTTFlags(IntEnum):
    RETAIN          = 0x01  # RETAIN = 1 (for PUBLISH)
    QOS1            = 0x02  # QoS level 1
    QOS2            = 0x04  # QoS level 2
    DUP             = 0x08  # DUP flag
    SUBSCRIBE_FLAG  = 0x02  # SUBSCRIBE requires QoS1 (0b0010)

## MQTT Connect Packet Flags Enum.
# CONNECT flags bitfield (MQTT v3.1.1)
# This enum contains the varius flags a MQTT CONNECT packet can contain.
class MQTTConnectFlags(IntEnum):
    RESERVED       = 0x01            # must be 0
    CLEAN_SESSION  = 0x02            # bit 1
    WILL_FLAG      = 0x04            # bit 2
    WILL_RETAIN    = 0x20            # bit 5
    PASSWORD       = 0x40            # bit 6
    USERNAME       = 0x80            # bit 7

class HeaderType(IntEnum):
    CONNECT = 0

## MQTT QOS Flags Enum.
# This enum contains the flags that identify the QoS level of a packet.
class MQTTWillQoS(IntEnum):
    QOS0    = (0 & 0x03) << 3   # Little hack to push the numbers in to bits 3 and 4
    QOS1    = (1 & 0x03) << 3
    QOS2    = (2 & 0x03) << 3

## MQTT Protocol Level Enum.
# This enum contains the flags that identify the MQTT Protocol version.
# Can be changed to a constant
class MQTTProtocolLevel(IntEnum):
    V3_1_1 = 0x04

## Function used to create a CONTROLL packet header.
def constructControlHeader(packetType: ControlHeaderType, variableHeaderSize: int, payloadSize: int, flags: int = 0x00) -> bytearray:
    fixedHeader = bytearray()

    fixedHeader += (packetType | flags).to_bytes(1, byteorder='big')

    remainingLength = variableHeaderSize + payloadSize

    fixedHeader += encodeVarint(remainingLength)

    return fixedHeader

## Function used to create the CONNECT packet variable header.
# Will be removed in further versions.
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

## MQTT Client Class.
# This class contains the code responsible for creating a connection
# to an MQTT broker, along with publishing data to the broker.
class MQTTSocketClient:
    ## MQTTSocketClient Constructor.
    def __init__(self, clientID: str, username: str = None, password: str = None, host: str = "homeassistant", port: int = 1883, tls=False, keepalive=60, timeout=10):
        self.clientID = clientID
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.tls = tls
        self.keepalive = keepalive
        self.timeout = timeout
        self.sock: socket.socket = None
        self.last_receive = time.time()
        self.last_send = time.time()
        self.connectionTime = None
        self.packet_id = 1

    ## Function to handle TLS wrapping.
    # Not yet implemented.
    def handle_tls(self):
        tlsHandler = ssl.create_default_context()
        return tlsHandler.wrap_socket(self.sock, server_hostname=self.host)

    ## Function to receive a packet byte by byte.
    # Function will receive n amount of bytes and return a full byte array of length n bytes.
    # n * 8bits
    def receiveAmountOfBytes(self, n: int) -> bytes:
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

    ## Function to receive an entire packet.
    # This function extracts the packet type, remaining length of the packet, and its payload.
    # The function returns the packet type and payload.
    # MQTT Packet Structure:
    # ---------------------------------------------
    # | Fixed Header | Remaining Length | Payload |
    # ---------------------------------------------
    def receive_packet(self) -> tuple[int, bytes]:
        byte1 = self.receiveAmountOfBytes(1)[0]
        packetType = byte1 & 0xF0

        remaining = decodeVarint(self.receiveAmountOfBytes)

        payload = self.receiveAmountOfBytes(remaining) if remaining else b''

        return packetType, payload

    ## Function to create a MQTT CONNECT Packet
    # MQTT CONNECT Packet Structure:
    # --------------------------------------------
    # | Fixed Header | Variable Header | Payload |
    # --------------------------------------------
    # Fixed Header: Packet Type and Flags - 1 Byte. Remaining Length 1-4 Bytes.
    # Variable Header: Flags - 1 Byte. Keep Alive - 2 Bytes.
    # Payload: Length Client ID - 2 Bytes. Client ID. Length Username - 2 Bytes. Username. Length Password - 2 Bytes. Password.
    # Returns the final CONNECT Packet
    def constructConnectPacket(self,  client_id: str, keepalive: int, username: str, password: str, will_topic: bytes, will_payload: bytes, will_retain: bool = True, clean_start: bool = True, will_qos: MQTTWillQoS = MQTTWillQoS.QOS1) -> bytes:

        # Construct CONNECT Packet Variable Header flags
        variableFlags = b'\x00'

        if clean_start:
            variableFlags = bitwiseOrForBytes(variableFlags, MQTTConnectFlags.CLEAN_SESSION.to_bytes(1, "big")) # cause supporting bitwise operations would make too much sense

        if username is not None:
            variableFlags = bitwiseOrForBytes(variableFlags, MQTTConnectFlags.USERNAME.to_bytes(1, "big"))

        if password is not None:
            variableFlags = bitwiseOrForBytes(variableFlags, MQTTConnectFlags.PASSWORD.to_bytes(1, "big"))


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

    ## Function to create a MQTT DISCONNECT Packet
    def constructDisconnectPacket(self) -> bytes:
        return bytes([ControlHeaderType.DISCONNECT, 0])

    ## Function to create a MQTT PINGREQ Packet
    def constructPingReqPacket(self) -> bytes:
        return bytes([ControlHeaderType.PINGREQ, 0x00])

    ## Function to construct a PUBLISH Packet.
    def constructPublishPacket(self, topic: str, payloadIn: str, qosLevel: MQTTFlags, qosPacketIdentifier: int, duplicate: bool = False) -> bytes:
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

    ## Function to create a MQTT PUBREL Packet
    def constructPubRelPacket(self, packetID: int) -> bytes:
        fixed_header = bytes([ControlHeaderType.PUBREL | 0x02, 0x02])
        variable_header = packetID.to_bytes(2, 'big')
        return fixed_header + variable_header

    ## Function to create a connection to a MQTT Broker.
    # Creates a connection to a MQTT Broker and varifies the connection.
    def connect(self):

        self.sock = socket.create_connection((self.host, self.port), self.timeout)

        if self.tls:
            self.sock = self.handle_tls()

        self.sock.settimeout(self.timeout)

        connectPacket = self.constructConnectPacket(self.clientID, self.keepalive, self.username, self.password, b"home/bme680/status", b"offline")

        print(connectPacket)
        print(f"Connect Packet Hex: {connectPacket.hex()}")

        self.sock.sendall(connectPacket)
        self.last_send = time.time()
        self.connectionTime = self.last_send

        print("Connect Packet Sent")

        # Confirm The Connection
        connackPacket = self.receive_packet()

        if connackPacket[0] == ControlHeaderType.CONNACK:
            print("Connack Packet Received")

        self.sock.sendall(self.constructPingReqPacket())
        type, payload = self.receive_packet()
        assert type == ControlHeaderType.PINGRESP and payload == b''

        print("CONNACK Packet Received")

    ## Function to disconnect from a MQTT Broker.
    # Contains logic to disconnect from a MQTT Broker and free the socket.
    # Will be refined in future versions.
    def disconnect(self):
        self.sock.sendall(self.constructDisconnectPacket())
        self.sock.close()
        self.sock = None

    ## Function to publish data to a MQTT topic.
    # Takes a MQTT topic, a topic data - str, int, float, bool, dict, and a QoS level.
    # As of now only QoS level 1 is supported and functional.
    # A PUBLISH packet is constructed using the constructor function.
    #
    # QoS 1 Structure:
    # PUBLISH Packet, Client -> Broker.
    # PUBACK Packet, Broker -> Client.
    # Duplicate PUBLISH packets will be sent until the PUBACK is received from the Broker.
    def publish(self, topicLevel: str, topicData, qosLevel: MQTTFlags):
        constructedTopics = {}

        if isinstance(topicData, (str, int, float, bool)):
            constructedTopics[topicLevel] = str(topicData)

        elif isinstance(topicData, dict):
            for key, value in topicData.items():
                constructedTopics[key] = str(value)

        successfulPackets = 0

        for key, value in constructedTopics.items():
            itterations = 1
            packet = self.constructPublishPacket(key, value, qosLevel, itterations, False)

            ## QoS level 1 logic.
            if qosLevel == MQTTFlags.QOS1:
                print("using qos1")
                while True:
                    self.sock.sendall(packet)
                    print(packet)
                    print(packet.hex())

                    inPacket = self.receive_packet()

                    if inPacket[0] == ControlHeaderType.PUBACK:
                        successfulPackets += 1
                        #print(f"PUBACK Packet Received. Successful Packets: {successfulPackets}")
                        break

                    itterations += 1
                    if itterations > MAX_QOS_PACKET_ATTEMPTS:
                        #print(f"Max QoS1 Send Attempts Reached.\nPacket: {packet}")
                        break

                    packet = self.constructPublishPacket(key, value, qosLevel, itterations, True)

            ## QoS level 2 logic.
            elif qosLevel == MQTTFlags.QOS2:
                print("using qos2")
                while True:
                    self.sock.sendall(packet)
                    print(f"Sent Packet: {packet}")
                    inPacket = self.receive_packet()

                    if inPacket[0] == ControlHeaderType.PUBREC:
                        print("PUBREC Packet Received")
                        self.sock.sendall(self.constructPubRelPacket(itterations + successfulPackets))
                        inPacket = self.receive_packet()
                        if inPacket[0] == ControlHeaderType.PUBCOMP:
                            print("PUBCOMP Packet Received")
                            successfulPackets += 1
                            break
                        else:
                            print("PUBCOMP Packet Not Received")
                            continue
                    else:
                        print("PUBREC Packet Not Received")
                        continue

                    itterations += 1
                    if itterations > MAX_QOS_PACKET_ATTEMPTS:
                        print(f"Max QoS  Send Attempts Reached.\nPacket: {packet}")
                        break

                    packet = self.constructPublishPacket(key, value, qosLevel, itterations + successfulPackets, False)

    ## Temporary function to publish all devices on the system
    def publishDevices(self):
        devices = find_iio_devices()

        for device in devices:
            deviceConfigs = device.generateConfigs(CLIENTID)

            for topic, config in deviceConfigs.items():
                self.publish(topic, json.dumps(config), MQTTFlags.QOS1)

            self.publish(device.availabilityTopic, "online", MQTTFlags.QOS1)
            self.publish(device.stateTopic, json.dumps(device.parse()), MQTTFlags.QOS1)

    ## Function to run code.
    # Temporary function to create a connection, verify connection, obtain sensor data, create a payload, publish data, then disconnect.
    # This function will be removed in further versions in favor of a proper API.
    def run(self):
        print("Starting MQTT Client")
        try:
            self.connect()
        except Exception as e:
            print(f"Failed to connect to MQTT server at {self.host}:{self.port}. Error: {e}")
            self.sock.close()
            quit()

        print("connection succeeded")

        sensorData = temp.parse_Data()

        """
        sensorData = {"temperature": 120, # get rid of this later
                "humidity": 41.3,
                "pressure": 1012.8,
                "gas": 12000}
        """

        bme680topic = "homeassistant/sensor/bme680/state"

        bme680config = {
            "homeassistant/sensor/bme680_temperature/config": {
                "name": "BME680 Temperature", "unique_id": "bme680_temperature",
                "state_topic": "homeassistant/sensor/bme680/state",
                "device_class": "temperature", "unit_of_measurement": "°F",
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

        payload = json.dumps(sensorData)
        """
        payload = json.dumps({"Temperature": 120,
                "Humidity": 41.3,
                "Pressure": 1012.8,
                "Gas": 12000})
        """


        for topic, config in bme680config.items():
            self.publish(topic, json.dumps(config), MQTTFlags.QOS1)

        self.publish("homeassistant/sensor/bme680/availability", "online", MQTTFlags.QOS1)
        self.publish("homeassistant/sensor/bme680/state", payload, MQTTFlags.QOS2)

        self.publishDevices()

        for i in range(20, 0, -1):
            print(f"Stopping in {i}...")
            time.sleep(1)

        self.disconnect()

## Test Code
if __name__ == "__main__":
    client = MQTTSocketClient(CLIENTID, username="oniic", password="Saltersimp5904", host=HOST, port=PORT)
    client.run()
