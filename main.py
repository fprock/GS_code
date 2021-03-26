# import serial
import sys
import time
import argparse
import struct
from datetime import datetime

def getTimeStamp():
    dateTimeObj = datetime.now()
    timestampStr = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S.%f)")
    return "Current Timestamp : " + timestampStr

def fakeSerial(inputFile):
    return inputFile.read(2)


rawPresFilePath = "logs/RawPresLog.txt"
compPresFilePath = "logs/CompPresLog.txt"
rawTempFilePath = "logs/RawTempLog.txt"
compTempFilePath = "logs/CompTempLog.txt"
rawHumFilePath = "logs/RawHumLog.txt"
compHumFilePath = "logs/CompTempLog.txt"
compAltFilePath = "logs/CompAltLog.txt"
baroMsgsFilePath = "Testdata.log"
dataLogFilePath = "logs/data.log"

rawPresFile = open(rawPresFilePath, "w")
rawPresFile.write("Received Raw Pressure Values\n")
compPresFile = open(compPresFilePath, "w")
compPresFile.write("Received calculated Pressure Values\n")
rawTempFile = open(rawTempFilePath, "w")
rawTempFile.write("Received Raw Temperature Values\n")
compTempFile = open(compTempFilePath, "w")
compTempFile.write("Received Raw Temperature Values\n")
rawHumFile = open(rawHumFilePath, "w")
rawHumFile.write("Received Raw Humidity Values\n")
compHumFile = open(compHumFilePath, "w")
compHumFile.write("Received calculated Humidity Values\n")
compAltFile = open(compAltFilePath, "w")
compAltFile.write("Received calculated Altitude Values\n")
dataFile = open(dataLogFilePath, "w")


def logData(dataType_count, data):
    if dataType_count == 0:
        print("Raw Pressure: " + str(data))
        rawPresFile.write("Raw Pressure: " + str(data) + "\n")
        dataFile.write("Raw Pressure: " + str(data) + "\n")
    elif dataType_count == 1:
        print("Raw Temperature: " + str(data))
        rawTempFile.write("Raw Temperature: " + str(data) + "\n")
        dataFile.write("Raw Temperature: " + str(data) + "\n")
    elif dataType_count == 2:
        print("Raw Humidity: " + str(data))
        rawHumFile.write("Raw Humidity: " + str(data) + "\n")
        dataFile.write("Raw Humidity: " + str(data) + "\n")
    elif dataType_count == 3:
        print("Calculated Pressure(Pa): " + str(data))
        compPresFile.write("Calculated Pressure(Pa): " + str(data) + "\n")
        dataFile.write("Calculated Pressure(Pa): " + str(data) + "\n")
    elif dataType_count == 4:
        print("Calculated Temperature(C): " + str(data))
        compTempFile.write("Calculated Temperature(C): " + str(data) + "\n")
        dataFile.write("Calculated Temperature(C): " + str(data) + "\n")
    elif dataType_count == 5:
        print("Calculated Humidity(%): " + str(data))
        compHumFile.write("Calculated Humidity(%): " + str(data) + "\n")
        dataFile.write("Calculated Humidity(%): " + str(data) + "\n")
    elif dataType_count == 6:
        print("Calculated Altitude: " + str(data))
        compAltFile.write("Calculated Altitude(m): " + str(data) + "\n")
        dataFile.write("Calculated Altitude(m): " + str(data) + "\n")
    else:
        print("IDK homie this shouldnt happen")
        print(str(dataType_count))


print("*BEGINNING PROGRAM*\n\n")

dataFile.write("*BEGINNING PROGRAM*\n\n")
parser = argparse.ArgumentParser(description="Parse bool")
parser.add_argument("-d", '-development', default=False, action="store_true")
args = parser.parse_args()


def main():
    state = "initial"
    baro_state = "payloadLength"
    payLoadLenFlag = False
    payLoadLen = 0
    payLoadCount = 0
    dataCount = 0
    dataType_count = 0
    convertingData = ""
    baroChecksumCount = 0
    if args.d:
        print("*ENTERING DEVELOPMENT MODE*\n")
        dataFile.write("*ENTERING DEVELOPMENT MODE*\n")
        baroMsgsFile = open(baroMsgsFilePath, "r")
        print("READING FROM FILE\n")
        dataFile.write("READING FROM FILE\n")
    else:
        ser = Serial('/dev/ttyUSB0', 9600)
        ser.flushInput()
        ser.flushOutput()
        print("READING FROM SERIAL\n")
        dataFile.write("READING FROM SERIAL\n")

    while True:
        if args.d:
            data_raw = fakeSerial(baroMsgsFile)
            if not data_raw:
                break
        else:
            data_raw = str(ser.readline())

        data_raw = data_raw.strip()
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
                convertingData = data_raw + convertingData
                dataCount = dataCount + 1
                if dataCount == 4:
                    data = struct.unpack('!f', bytes.fromhex(convertingData))[0]
                    logData(dataType_count, data)
                    dataType_count = dataType_count + 1
                    dataCount = 0
                    data = ""
                    convertingData = ""
                payLoadCount = payLoadCount + 1
                if payLoadCount == payLoadLen:
                    print("END OF PAYLOAD")
                    dataFile.write("END OF PAYLOAD\n")
                    state = "barochecksum"
                    baro_state = "payloadLength"
                    baroChecksumCount = 0
                    payLoadCount = 0
                    payLoadLen = 0
                    payLoadCount = 0
                    dataType_count = 0
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
        elif state == "barochecksum":

            baroChecksumCount = baroChecksumCount + 1
            print("Checksum #" + str(baroChecksumCount) + ": " + data_raw)
            if baroChecksumCount == 2:
                print("\n")
                state = "initial"
        else:
            print(
                f"ERROR: missing starting flag, discarding incoming data({data_raw}) and waiting till next start flags")
            dataFile.write(
                "ERROR: missing starting flag, discarding incoming data(" + data_raw + ") and waiting till next "
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


main()
