import pprint
import struct
import binascii

def readUBX(readbytes):
    RELPOSNED = b'3c'
    PVT = b'07'
    POSLLH = b'02'
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
    tempBytes = ""
    ackPacket = ackPacket[6:98]
    pospvt = dict()

    # iTOW
    byteoffset = 0
    for i in range(0, 4):
        tempBytes += bytes.decode(ackPacket[byteoffset + i])
    print(tempBytes)
    pospvt["iTOW"] = int(tempBytes, 16)
    tempBytes = ""

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

    #validity Flags
    byteoffset = 11
    print(ackPacket[byteoffset])
    bytevalue = bytes.decode(ackPacket[byteoffset])
    print(bytevalue)
    binary_string = binascii.unhexlify(bytevalue)
    print(binary_string)

    # PosLon
    byteoffset = 24
    bytevalue = ackPacket[byteoffset]
    for i in range(1, 4):
        bytevalue += ackPacket[byteoffset + i]

    print("lon Bytes: " + str(bytevalue))
    pospvt["Longitude"] = int(bytevalue, 16)

    # PosLat
    byteoffset = 28
    bytevalue = ackPacket[byteoffset]
    for i in range(1, 4):
        bytevalue += ackPacket[byteoffset + i]
    print("lat Bytes: " + str(bytevalue))
    pospvt["Latitude"] = int(bytevalue, 16)

    # posHeight
    byteoffset = 32
    bytevalue = ackPacket[byteoffset]
    for i in range(1, 4):
        bytevalue += ackPacket[byteoffset + i]
    print("height Bytes: " + str(bytevalue))
    pospvt["Height"] = int(bytevalue, 16)

    # Height above mean sea level
    byteoffset = 36
    bytevalue = ackPacket[byteoffset]
    for i in range(1, 4):
        bytevalue += ackPacket[byteoffset + i]
    print("hMSL Bytes: " + str(bytevalue))
    pospvt["hMSL"] = int(bytevalue, 16)

    # Ground Speed
    byteoffset = 60
    bytevalue = ackPacket[byteoffset]
    for i in range(1, 4):
        bytevalue += ackPacket[byteoffset + i]
    print("gSpeed Bytes: " + str(bytevalue))
    pospvt["gSpeed"] = int(bytevalue, 16)

    # Heading of motion
    byteoffset = 64
    bytevalue = ackPacket[byteoffset]
    for i in range(1, 4):
        bytevalue += ackPacket[byteoffset + i]
    print("headMot Bytes: " + str(bytevalue))
    pospvt["headMot"] = int(bytevalue, 16)

    return pospvt
