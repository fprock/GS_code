import binascii
import struct


def HexValue_to_float(HexValue):
    if len(HexValue) < 16:
        for x in range(len(HexValue), 16):
            HexValue = "0" + HexValue
    return struct.unpack('<f', binascii.unhexlify(HexValue))
    #return HexValue