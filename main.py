# import serial
import sys
from classes import CompHumClass
import time
import argparse
import struct

def fakeSerial(inputFile):
    return inputFile.readline()

rawPresFilePath = "logs/RawPresLog.txt"
compPresFilePath = "logs/CompPresLog.txt"
rawTempFilePath = "logs/RawTempLog.txt"
compTempFilePath = "logs/CompTempLog.txt"
rawHumFilePath = "logs/RawHumLog.txt"
compHumFilePath = "logs/CompTempLog.txt"
baroMsgsFilePath = "baroMessages.dat"

rawPresFile = open(rawPresFilePath, "w")
compPresFile = open(compPresFilePath, "w")
rawTempFile = open(rawTempFilePath, "w")
compTempFile = open(compTempFilePath, "w")
rawHumFile = open(rawHumFilePath, "w")
compHumFile = open(compHumFilePath, "w")

print("*BEGINNING PROGRAM*\n\n")
parser = argparse.ArgumentParser(description="Parse bool")
parser.add_argument("-d", '-development', default=False, action="store_true")
args = parser.parse_args()


def main():
    firstFlag = False
    secondFlag = False
    baroFlag = False
    messageFlag = False
    payLoadLenFlag = False
    payLoadLen = 0
    payLoadCount = 0
    dataCount = 0
    convertingData = ""
    if args.d:
        print("*ENTERING DEVELOPMENT MODE*\n")
        baroMsgsFile = open(baroMsgsFilePath, "r")
    else:
        ser = Serial('/dev/ttyUSB0', 9600)
        ser.flushInput()
        ser.flushOutput()
    print("READING FROM FILE\n")
    while True:
        if args.d:
            data_raw = fakeSerial(baroMsgsFile)
            if not data_raw:
                break
        else:
            print("READING FROM SERIAL")
            data_raw = str(ser.readline())

        data_raw = data_raw.strip()
        if data_raw == "BB" and not firstFlag and not baroFlag and not messageFlag:
            print("First start flag received")
            firstFlag = True
            baroFlag = False
            messageFlag = False
            payLoadLenFlag = False
            payLoadLen = 0
            payLoadCount = 0
        elif data_raw == "AE" and firstFlag and not secondFlag and not baroFlag and not messageFlag:
            print("Second start flag received")
            secondFlag = True
            firstFlag = False
        elif secondFlag:
            if data_raw == "00":
                print("Message Class received")
                messageFlag = True
                firstFlag = False
                secondFlag = False
            elif data_raw == "01":
                print("Barometer Class received")
                baroFlag = True
                firstFlag = False
                secondFlag = False
            else:
                print("Invalid class received discarding data until next start")
                firstFlag = False
                secondFlag = False
        elif baroFlag:
            if payLoadLenFlag:
                convertingData = data_raw + convertingData
                dataCount = dataCount + 1
                if dataCount == 4:
                    print("Attempting to convert: " + convertingData)
                    data = struct.unpack('!f', bytes.fromhex(convertingData))[0]
                    print(data)
                    dataCount = 0
                    data = ""
                    convertingData = ""
                payLoadCount = payLoadCount + 1
                if payLoadCount == payLoadLen:
                    print("END OF PAYLOAD")
                    payLoadCount = 0
                    firstFlag = False
                    secondFlag = False
                    baroFlag = False
                    messageFlag = False
                    payLoadLenFlag = False
                    payLoadLen = 0
                    payLoadCount = 0
            else:
                payLoadLenFlag = True
                payLoadLen = int(data_raw, 16)
                print("Barometer payload length is " + str(payLoadLen) + " bytes")
        elif messageFlag:
            if payLoadLenFlag:
                #message data conversion

                payLoadCount = payLoadCount + 1
                if payLoadCount == payLoadLen:
                    print("END OF PAYLOAD")
                    payLoadCount = 0
            else:
                payLoadLenFlag = True
                payLoadLen = int(data_raw, 16)
                print("Message payload length is " + str(payLoadLen) + " bytes")
        else:
            print("ERROR: missing starting flag, discarding incoming data and waiting till next start flags")
            firstFlag = False
            secondFlag = False

    if args.d:
        baroMsgsFile.close()

    rawPresFile.close()
    compPresFile.close()
    rawTempFile.close()
    compTempFile.close()
    rawHumFile.close()
    compHumFile.close()


main()
