import pprint
import struct
import binascii
from bitarray import *

def readUBX(readbytes):
    PVT = b'07'
    msg = dict()
    j = 0
    while j < len(readbytes):
        i = 0
        payloadlength = 0
        ackPacket = [b'B5', b'62', b'01', b'00', b'00', b'00']
        while i < payloadlength + 8:

            if j < len(readbytes):
                incoming_byte = readbytes[j]
                j += 1
            else:
                break
            if (i < 3) and (incoming_byte == ackPacket[i]):
                i += 1
            elif i == 3:
                ackPacket[i] = incoming_byte
                i += 1
            elif i == 4:
                ackPacket[i] = incoming_byte
                i += 1
            elif i == 5:
                ackPacket[i] = incoming_byte
                payloadlength = int(ackPacket[4], 16) + int(ackPacket[5], 16)
                i += 1
            elif (i > 5):
                ackPacket.append(incoming_byte)
                i += 1
        if checksum(ackPacket, payloadlength):
            if ackPacket[3] == PVT:
                msg.update(persePVT(ackPacket))
            else:
                print("Class does not line up with PVT")
    return msg


def checksum(ackPacket, payloadlength):
    CK_A = 0
    CK_B = 0
    for i in range(2, payloadlength + 6):
        CK_A = CK_A + int(ackPacket[i], 16)
        CK_B = CK_B + CK_A
    CK_A &= 0xff
    CK_B &= 0xff
    if (CK_A == int(ackPacket[-2], 16)) and (
            CK_B == int(ackPacket[-1], 16)):
        print("GPS Checksum valid")
        return True
    else:
        print("GPS Checksum invalid")
        return False


def persePVT(ackPacket):
    ackPacket = ackPacket[6:98]
    pospvt = dict()

    # iTOW
    byteoffset = 0
    bytevalue = ackPacket[byteoffset]
    for i in range(1, 4):
        bytevalue += ackPacket[byteoffset + i]
    bytevalue = str(bytevalue)[2:10].upper()
    pospvt["iTOW"] = (struct.unpack('<I', bytes.fromhex(bytevalue))[0])

    # Year
    byteoffset = 4
    bytevalue = ackPacket[byteoffset + 1]
    bytevalue += ackPacket[byteoffset]
    pospvt["Year"] = int(bytevalue, 16)

    # month day hour min sec
    byteoffset = 6
    bytevalue = ackPacket[byteoffset]
    i = 0
    for key in ("Month", "Day", "Hour", "Minute", "Second"):
        bytevalue = ackPacket[byteoffset + i]
        pospvt[key] = int(bytevalue, 16)
        i += 1

    # validity Flags
    byteoffset = 11
    bytevalue = bytes.decode(ackPacket[byteoffset])
    validbits = bin(int(bytevalue, 16)).zfill(8)
    pospvt["Valid Date"] = validbits[7]
    pospvt["Valid Time"] = validbits[6]
    pospvt["Fully Resolved"] = validbits[5]
    pospvt["Valid Mag"] = validbits[4]

    # time accuracy esitmate
    byteoffset = 12
    bytevalue = ackPacket[byteoffset]
    for i in range(1, 4):
        bytevalue += ackPacket[byteoffset + i]
    bytevalue = str(bytevalue)[2:10].upper()
    pospvt["tAcc"] = (struct.unpack('<I', bytes.fromhex(bytevalue))[0] )

    # Fraction of a second
    byteoffset = 16
    bytevalue = ackPacket[byteoffset]
    for i in range(1, 4):
        bytevalue += ackPacket[byteoffset + i]
    bytevalue = str(bytevalue)[2:10].upper()
    pospvt["nano"] = (struct.unpack('<i', bytes.fromhex(bytevalue))[0])

    #fix type
    byteoffset = 20
    bytevalue = bytes.decode(ackPacket[byteoffset])
    if bytevalue == '00':
        pospvt["Fix Type"] = "No Fix"
    elif bytevalue == '01':
        pospvt["Fix Type"] = "Dead reckoning only"
    elif bytevalue == '02':
        pospvt["Fix Type"] = "2D-Fix"
    elif bytevalue == '03':
        pospvt["Fix Type"] = "3D-Fix"
    elif bytevalue == '04':
        pospvt["Fix Type"] = "GNSS + Dead reckoning combined"
    elif bytevalue == '05':
        pospvt["Fix Type"] = "Time only fix"

    # PosLon
    byteoffset = 24
    bytevalue = ""
    bytevalue = ackPacket[byteoffset]
    for i in range(1, 4):
        bytevalue += ackPacket[byteoffset + i]
    bytevalue = str(bytevalue)[2:10].upper()
    pospvt["Longitude"] = (struct.unpack('<i', bytes.fromhex(bytevalue))[0] * 10**(-7))

    # PosLat
    byteoffset = 28
    bytevalue = ""
    bytevalue = ackPacket[byteoffset]
    for i in range(1, 4):
        bytevalue += ackPacket[byteoffset + i]
    bytevalue = str(bytevalue)[2:10].upper()
    pospvt["Latitude"] = (struct.unpack('<i', bytes.fromhex(bytevalue))[0] * 10**(-7))

    # posHeight
    byteoffset = 32
    bytevalue = ackPacket[byteoffset]
    for i in range(1, 4):
        bytevalue += ackPacket[byteoffset + i]
    bytevalue = str(bytevalue)[2:10].upper()
    pospvt["Height"] = (struct.unpack('<i', bytes.fromhex(bytevalue))[0]) * 10 ** (-3)

    # Height above mean sea level
    byteoffset = 36
    bytevalue = ackPacket[byteoffset]
    for i in range(1, 4):
        bytevalue += ackPacket[byteoffset + i]
    bytevalue = str(bytevalue)[2:10].upper()
    pospvt["hMSL"] = (struct.unpack('<i', bytes.fromhex(bytevalue))[0]) * 10 ** (-3)

    # Horizontal accuracy estimate
    byteoffset = 40
    bytevalue = ackPacket[byteoffset]
    for i in range(1, 4):
        bytevalue += ackPacket[byteoffset + i]
    bytevalue = str(bytevalue)[2:10].upper()
    pospvt["hAcc"] = (struct.unpack('<I', bytes.fromhex(bytevalue))[0]) * 10 ** (-3)

    # Vertical accuracy estimate
    byteoffset = 44
    bytevalue = ackPacket[byteoffset]
    for i in range(1, 4):
        bytevalue += ackPacket[byteoffset + i]
    bytevalue = str(bytevalue)[2:10].upper()
    pospvt["vAcc"] = (struct.unpack('<I', bytes.fromhex(bytevalue))[0]) * 10 ** (-3)

    # NED north velocity
    byteoffset = 48
    bytevalue = ackPacket[byteoffset]
    for i in range(1, 4):
        bytevalue += ackPacket[byteoffset + i]
    bytevalue = str(bytevalue)[2:10].upper()
    pospvt["velN"] = (struct.unpack('<i', bytes.fromhex(bytevalue))[0]) * 10 ** (-3)

    # NED east velocity
    byteoffset = 52
    bytevalue = ackPacket[byteoffset]
    for i in range(1, 4):
        bytevalue += ackPacket[byteoffset + i]
    bytevalue = str(bytevalue)[2:10].upper()
    pospvt["velE"] = (struct.unpack('<i', bytes.fromhex(bytevalue))[0]) * 10 ** (-3)

    # NED down velocity
    byteoffset = 56
    bytevalue = ackPacket[byteoffset]
    for i in range(1, 4):
        bytevalue += ackPacket[byteoffset + i]
    bytevalue = str(bytevalue)[2:10].upper()
    pospvt["velD"] = (struct.unpack('<i', bytes.fromhex(bytevalue))[0]) * 10 ** (-3)

    # Ground Speed
    byteoffset = 60
    bytevalue = ackPacket[byteoffset]
    for i in range(1, 4):
        bytevalue += ackPacket[byteoffset + i]
    bytevalue = str(bytevalue)[2:10].upper()
    pospvt["gSpeed"] = (struct.unpack('<i', bytes.fromhex(bytevalue))[0]) * 10 ** (-3)

    # Heading of motion
    byteoffset = 64
    bytevalue = ackPacket[byteoffset]
    for i in range(1, 4):
        bytevalue += ackPacket[byteoffset + i]
    bytevalue = str(bytevalue)[2:10].upper()
    pospvt["headMot"] = struct.unpack('<i', bytes.fromhex(bytevalue))[0]*10**(-5)

    return pospvt
