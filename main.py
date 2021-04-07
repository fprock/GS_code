import sys
import argparse
import multiprocessing as mp
from threading import *
from datetime import datetime
# from importer import *
# from importer import receiver
from GUI import GUI_GO, presQueue, tempQueue, humQueue, altQueue, GPSQueue
from readUBX import *

from fakeserial import *
from fakeserial import receiver


def getTimeStamp():
    dateTimeObj = datetime.now()
    timestampStr = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S.%f)")
    return "Current Timestamp : " + timestampStr


def validateBaroChecksum(Baro_Bytes, Baro_checksumBytes):
    CK_A = 0
    CK_B = 0
    for i in range(0, 28):
        CK_A = CK_A + int(Baro_Bytes[i], 16)
        CK_B = CK_B + CK_A
    CK_A &= 0xff
    CK_B &= 0xff
    if (CK_A == int(Baro_checksumBytes[0], 16)) and (CK_B == int(Baro_checksumBytes[1], 16)):
        print("Barometer Checksum valid")
        return True
    else:
        print("Barometer Checksum invalid")
        return False


rawPresFilePath = "logs/decoded/RawPresLog.txt"
compPresFilePath = "logs/decoded/CompPresLog.txt"
rawTempFilePath = "logs/decoded/RawTempLog.txt"
compTempFilePath = "logs/decoded/CompTempLog.txt"
rawHumFilePath = "logs/decoded/RawHumLog.txt"
compHumFilePath = "logs/decoded/CompHumLog.txt"
compAltFilePath = "logs/decoded/CompAltLog.txt"
baroMsgsFilePath = "HexFile.txt"
dataLogFilePath = "logs/decoded/data.txt"
byteLogFilePath = "logs/decoded/byteLog.txt"

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

global GUI_iterater
GUI_iterater = 0

def logData(dataType_count, data, GUI_iterater):
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
        presQueue.put(data[3])
    elif dataType_count == 4:
        print("Calculated Temperature(C): " + str(data[4]))
        compTempFile.write(str(data[4]) + "\n")
        dataFile.write("Calculated Temperature(C): " + str(data[4]) + "\n")
        tempQueue.put(data[4])
    elif dataType_count == 5:
        print("Calculated Humidity(%): " + str(data[5]))
        compHumFile.write(str(data[5]) + "\n")
        dataFile.write("Calculated Humidity(%): " + str(data[5]) + "\n")
        humQueue.put(data[5])
    elif dataType_count == 6:
        print("Calculated Altitude: " + str(data[6]))
        compAltFile.write(str(data[6]) + "\n")
        dataFile.write("Calculated Altitude(m): " + str(data[6]) + "\n")
        altQueue.put(data[6])
    else:
        print("IDK homie this shouldnt happen")


print("*BEGINNING PROGRAM*\n\n")

dataFile.write("*BEGINNING PROGRAM*\n\n")
parser = argparse.ArgumentParser(description="Parse bool")
parser.add_argument("-d", '-development', default=False, action="store_true")
args = parser.parse_args()

# serOrFile = args.d
# Importer = Thread(target=importSerial, args=(serOrFile,))
# Importer.start()


Fake = Thread(target=fakeserial, args=("HexFile_withtime.txt",))
Fake.start()


GUI = Thread(target=GUI_GO)
GUI.start()



def main():
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
    GUI_iterater = 0

    if args.d:
        print("*ENTERING DEVELOPMENT MODE*\n")
        dataFile.write("*ENTERING DEVELOPMENT MODE*\n")
        #baroMsgsFile = open(baroMsgsFilePath, "r")
        print("READING FROM FILE\n")
        dataFile.write("READING FROM FILE\n")
    else:

        print("READING FROM SERIAL\n")
        dataFile.write("READING FROM SERIAL\n")

    while True:
        data_raw = ""
        data_raw = receiver.recv()
        # print(data_raw)
        if len(data_raw) == 2:
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
                            logData(i, data, GUI_iterater)
                    else:
                        print("CHECKSUM INVALID IGNORING DATA")
                    GUI_iterater += 1
                    if GUI_iterater == 5:
                        GUI_iterater = 0
                    print("\n")
                    state = "initial"
                    data = []
                    baroBytes = []
                    baroChecksum = []
            elif state == "initial" and data_raw == "B5":
                print("Intercepting GPS data")
                gpsByte_string = gpsByte_string + data_raw
                gps_bytes.append(bytes(data_raw, 'UTF-8'))
                state = "readGPS"
                i = 1
            elif state == "readGPS":
                gpsByte_string = gpsByte_string + data_raw
                gps_bytes.append(bytes(data_raw, 'UTF-8'))
                i = i + 1
                if i == 100:
                    state = "initial"
                    GPSdict = readUBX(gps_bytes)
                    dataFile.write("\nGPS DATA:\n")
                    GPSQueue.put(GPSdict)
                    for key, value in GPSdict.items():
                        print(key + ":", value)
                        dataFile.write(str(key) + ": " + str(value) + "\n")
                    print("\n")
                    gps_bytes = []
                    gpsByte_string = ""
            else:
                print(
                    f"ERROR: missing starting flag, discarding incoming data({data_raw}) and waiting till next start flags")
                dataFile.write(
                    "ERROR: missing starting flag, discarding incoming data(" + str(data_raw) + ") and waiting till next start flags\n")
        else:
            continue


try:
    main()
except KeyboardInterrupt:
    # Importer.join()
    Fake.join()
    GUI.join()
    rawPresFile.close()
    compPresFile.close()
    rawTempFile.close()
    compTempFile.close()
    rawHumFile.close()
    compHumFile.close()
    dataFile.close()

    sys.exit(0)
