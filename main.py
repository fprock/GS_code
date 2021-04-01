import serial
import sys
import time
import argparse
import struct
import multiprocessing as mp
from datetime import datetime
from importer import importSerial
from GUI import GUI_GO
from readUBX import *
import variables
from queue import *



def getTimeStamp():
    dateTimeObj = datetime.now()
    timestampStr = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S.%f)")
    return "Current Timestamp : " + timestampStr


def fakeSerial(inputFile):
    return inputFile.read(2)


def validateBaroChecksum(Baro_Bytes, Baro_checksumBytes):
    CK_A = 0
    CK_B = 0
    for i in range(0, 28):
        CK_A = CK_A + int(Baro_Bytes[i], 16)
        CK_B = CK_B + CK_A
    CK_A &= 0xff
    CK_B &= 0xff
    print("Cal CK_A = " + str(CK_A) + " Actual CH_A = " + str(int(Baro_checksumBytes[0], 16)) + " Cal CK_B = " + str(
        CK_B) + " Actual CH_B = " + str(int(Baro_checksumBytes[1], 16)))
    if (CK_A == int(Baro_checksumBytes[0], 16)) and (CK_B == int(Baro_checksumBytes[1], 16)):
        print("Barometer Checksum valid")
        return True
    else:
        print("Barometer Checksum invalid")
        return True


rawPresFilePath = "logs/RawPresLog.txt"
compPresFilePath = "logs/CompPresLog.txt"
rawTempFilePath = "logs/RawTempLog.txt"
compTempFilePath = "logs/CompTempLog.txt"
rawHumFilePath = "logs/RawHumLog.txt"
compHumFilePath = "logs/CompHumLog.txt"
compAltFilePath = "logs/CompAltLog.txt"
baroMsgsFilePath = "HexFile.txt"
dataLogFilePath = "logs/data.log"
byteLogFilePath = "logs/byteLog.txt"

rawPresFile = open(rawPresFilePath, "w")
rawPresFile.write("Received Raw Pressure Values\n")
compPresFile = open(compPresFilePath, "w")
compPresFile.write("0\n")
rawTempFile = open(rawTempFilePath, "w")
rawTempFile.write("Received Raw Temperature Values\n")
compTempFile = open(compTempFilePath, "w")
compTempFile.write("0\n")
rawHumFile = open(rawHumFilePath, "w")
rawHumFile.write("Received Raw Humidity Values\n")
compHumFile = open(compHumFilePath, "w")
compHumFile.write("0\n")
compAltFile = open(compAltFilePath, "w")
compAltFile.write("0\n")
dataFile = open(dataLogFilePath, "w")
byteFile = open(byteLogFilePath, "w")
global hexBytes

def logData(dataType_count, data):
    if dataType_count == 0:
        print("Raw Pressure: " + str(data[0]))
        rawPresFile.write("Raw Pressure: " + str(data[0]) + "\n")
        dataFile.write("Raw Pressure: " + str(data[0]) + "\n")
    elif dataType_count == 1:
        print("Raw Temperature: " + str(data[1]))
        rawTempFile.write("Raw Temperature: " + str(data[1]) + "\n")
        dataFile.write("Raw Temperature: " + str(data[1]) + "\n")
    elif dataType_count == 2:
        print("Raw Humidity: " + str(data[2]))
        rawHumFile.write("Raw Humidity: " + str(data[2]) + "\n")
        dataFile.write("Raw Humidity: " + str(data[2]) + "\n")
    elif dataType_count == 3:
        print("Calculated Pressure(Pa): " + str(data[3]))
        compPresFile.write(str(data[3]) + "\n")
        dataFile.write("Calculated Pressure(Pa): " + str(data[3]) + "\n")
    elif dataType_count == 4:
        print("Calculated Temperature(C): " + str(data[4]))
        compTempFile.write(str(data[4]) + "\n")
        dataFile.write("Calculated Temperature(C): " + str(data[4]) + "\n")
    elif dataType_count == 5:
        print("Calculated Humidity(%): " + str(data[5]))
        compHumFile.write(str(data[5]) + "\n")
        dataFile.write("Calculated Humidity(%): " + str(data[5]) + "\n")
    elif dataType_count == 6:
        print("Calculated Altitude: " + str(data[6]))
        compAltFile.write(str(data[6]) + "\n")
        dataFile.write("Calculated Altitude(m): " + str(data[6]) + "\n")
    else:
        print("IDK homie this shouldnt happen")
        # print(str(dataType_count))


print("*BEGINNING PROGRAM*\n\n")

dataFile.write("*BEGINNING PROGRAM*\n\n")
parser = argparse.ArgumentParser(description="Parse bool")
parser.add_argument("-d", '-development', default=False, action="store_true")
args = parser.parse_args()
if not args.d:
    ser = serial.Serial('/dev/ttyUSB0', 9600)

variables.init()

def main():
    Importer = mp.Process(target=importSerial)
    Importer.start()

    #GUI = mp.Process(target=GUI_GO)
    #GUI.start()

    state = "initial"
    baro_state = "payloadLength"
    payLoadLenFlag = False
    payLoadLen = 0
    payLoadCount = 0
    dataCount = 0
    dataType_count = 1
    convertingData = ""
    baroChecksumCount = 0
    data = []
    baroBytes = []
    gps_bytes = []
    gpsByte_string = ""
    baroChecksum = []

    if args.d:
        print("*ENTERING DEVELOPMENT MODE*\n")
        dataFile.write("*ENTERING DEVELOPMENT MODE*\n")
        baroMsgsFile = open(baroMsgsFilePath, "r")
        print("READING FROM FILE\n")
        dataFile.write("READING FROM FILE\n")
    else:

        print("READING FROM SERIAL\n")
        dataFile.write("READING FROM SERIAL\n")

    while True:
        print(str(variables.hexBytes.get()))
        data_raw = ""
        if args.d:
            data_raw = fakeSerial(baroMsgsFile)
            if not data_raw:
                break
        else:
            data_raw = ser.read(1)
            print(str(data_raw))

        if data_raw == "BB" and state == "initial":  # First starting byte
            print(getTimeStamp())
            dataFile.write("\n" + getTimeStamp() + "\n")
            print("First FPROCK start flag received")
            dataFile.write("First FPROCK start flag received\n")
            state = "baroFirst"
            payLoadLen = 0
            payLoadCount = 0
        elif data_raw == "AE" and state == "baroFirst":  # Second stating byte
            print("Second FPROCK start flag received")
            dataFile.write("Second FPROCK start flag received\n")
            state = "Class"
        elif state == "Class":  # finding class
            if data_raw == "00":  # message class
                print("Message Class received")
                dataFile.write("Message Class received\n")
                state = "messageClass"
            elif data_raw == "01":  # baro class
                print("Barometer Class received")
                dataFile.write("Barometer Class received\n")
                state = "baroClass"
            else:
                print("Invalid class received discarding data until next start")
                dataFile.write("Invalid class received discarding data until next start\n")
                state = "initial"
        elif state == "baroClass":
            if baro_state == "payload":
                baroBytes.append(data_raw)
                convertingData = data_raw + convertingData
                dataCount = dataCount + 1
                if dataCount == 4:
                    data.append(struct.unpack('!f', bytes.fromhex(convertingData))[0])
                    dataType_count = dataType_count + 1
                    dataCount = 0
                    convertingData = ""
                payLoadCount = payLoadCount + 1
                if payLoadCount == payLoadLen:
                    print("PAYLOAD READ IN")
                    dataFile.write("END OF PAYLOAD\n")
                    state = "barochecksum"
                    baro_state = "payloadLength"
                    baroChecksumCount = 0
                    payLoadCount = 0
                    payLoadLen = 0
                    payLoadCount = 0
                    dataType_count = 1
            elif baro_state == "payloadLength":
                payLoadLenFlag = True
                payLoadLen = int(data_raw, 16)
                print("Barometer payload length is " + str(payLoadLen) + " bytes")
                dataFile.write("Barometer payload length is " + str(payLoadLen) + " bytes\n")
                baro_state = "payload"
        elif state == "messageClass":
            if payLoadLenFlag:
                # message data conversion

                payLoadCount = payLoadCount + 1
                if payLoadCount == payLoadLen:
                    print("END OF PAYLOAD")
                    dataFile.write("END OF PAYLOAD\n")
                    payLoadCount = 0
            else:
                payLoadLenFlag = True
                payLoadLen = int(data_raw, 16)
                print("Message payload length is " + str(payLoadLen) + " bytes")
                dataFile.write("Message payload length is " + str(payLoadLen) + " bytes\n")
                baroBytes.append(data_raw)
        elif state == "barochecksum":
            baroChecksumCount = baroChecksumCount + 1
            baroChecksum.append(data_raw)
            if baroChecksumCount == 2:
                if validateBaroChecksum(baroBytes, baroChecksum):
                    for i in range(0, 7):
                        logData(i, data)
                else:
                    print("CHECKSUM INVALID IGNORING DATA")
                print("\n")
                state = "initial"
                data = []
                baroBytes = []
                baroChecksum = []
        elif state == "initial" and data_raw == "B5----":
            print("Intercepting GPS data")
            gpsByte_string = gpsByte_string + data_raw
            gps_bytes.append(bytes(data_raw, 'UTF-8'))
            state = "readGPS"
            i = 1
            print("GPS Byte #" + str(i) + ": " + data_raw)
        elif state == "readGPS":
            gpsByte_string = gpsByte_string + data_raw
            gps_bytes.append(bytes(data_raw, 'UTF-8'))
            i = i + 1
            print("GPS Byte #" + str(i) + ": " + data_raw)
            if i == 100:
                state = "initial"
                GPSdict = readUBX(gps_bytes)
                for key, value in GPSdict.items():
                    print(key + ":", value)
                print("\n")
                gps_bytes = []
                gpsByte_string = ""
        else:
            print(
                f"ERROR: missing starting flag, discarding incoming data({data_raw}) and waiting till next start flags")
            dataFile.write(
                "ERROR: missing starting flag, discarding incoming data(" + str(data_raw) + ") and waiting till next "
                                                                                            "start flags\n")

    if args.d:
        baroMsgsFile.close()

    rawPresFile.close()
    compPresFile.close()
    rawTempFile.close()
    compTempFile.close()
    rawHumFile.close()
    compHumFile.close()
    dataFile.close()


try:
    main()
except KeyboardInterrupt:
    GUI.join()
    Importer.join()
    sys.exit(0)
