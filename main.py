# import serial
import sys
from classes import CompHumClass
import time
import argparse


def fakeSerial(inputFile):
    #return bytes.fromhex(inputFile.readline())
    return inputFile.readline()

# pseudo code for validation

#   if inputArr(0) == start_char1
#         if inputArr(1) == start_char2 {
#             if inputArr(2) == msg_classX {
#                 msg.class = msg_classX
#                 msg.payloadLength = inputArr(3)
#                 msg.payload = inputArr(4:(msg.payloadLength - 1))
#                 msg.CK_A = inputArr(payloadOffset + msg.payloadLength)
#                 msg.CK_B = inputArr(payloadOffset + msg.payloadLength + 1)
#                 msg.valid = fletchersAlgorithm(msg) //if recieved CK_A and CK_B do not match calculated values
#                                                     //then return false
#             }
#             elif inputArr(2) == msg_classY {
#                 msg.class = msg_classY
#                 ~
#                 ~
#                 ~
#             }
#             //more classes
#             ~
#             ~
#             ~
#             else {
#                 msg.valid = false
#             }
#         else {
#             msg.valid = false
#         }
#     else {
#         msg.valid = false
#     }
rawPresFilePath = "logs/RawPresLog.txt"
compPresFilePath = "logs/CompPresLog.txt"
rawTempFilePath = "logs/RawTempLog.txt"
compTempFilePath = "logs/CompTempLog.txt"
rawHumFilePath = "logs/RawHumLog.txt"
compHumFilePath = "logs/CompTempLog.txt"

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
    global baroMsgsFile
    if args.d:
        print("*ENTERING DEVELOPMENT MODE*\n")
        baroMsgsFilePath = "baroMessages.dat"
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
        if data_raw == "BB":
            print("First barometer flag received")
            firstFlag = True
        elif data_raw == "AE" and firstFlag:
            print("Second barometer flag received")
            secondFlag = True
        elif secondFlag:
            print(data_raw)
        else:
            print("ERROR: missing starting flag, discarding incoming data and waiting till next start flags")
            firstFlag, secondFlag = False

    if args.d:
        baroMsgsFile.close()

    rawPresFile.close()
    compPresFile.close()
    rawTempFile.close()
    compTempFile.close()
    rawHumFile.close()
    compHumFile.close()


main()
