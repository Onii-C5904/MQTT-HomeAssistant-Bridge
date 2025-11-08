'''
10/8/2025
Kristijan Stojanovski

Various helper functions
'''

import struct



def getFileContent(filename)->str:
    """
    Displays the content of a given file to the console.
    """
    try:
        with open(filename, 'r') as f:
            content = f.read()
            return str(content)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

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

def encodeVarint(n: int) -> bytes:
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

def decodeVarint(receive_function) -> int:
    multiplier = 1
    value = 0
    while True:
        b = receive_function(1)
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