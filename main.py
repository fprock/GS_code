#import serial
from classes import CompHumClass
import time

#pseudo code for validation

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



debug = True

def fakeserial(inputfile):
    return bytes.fromhex(inputfile.readline())


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

firstLine = False
if debug:
    baroMsgsFilePath = "baroMessages.dat"
    baroMsgsFile = open(baroMsgsFilePath, "r")
else:
    ser = serial.Serial('/dev/ttyUSB0', 9600)
    ser.flushInput()
    ser.flushOutput()
while True:
    if debug:
        data_raw = fakeserial(baroMsgsFile)
        if not data_raw:
            break
    else:
        data_raw = str(ser.readline())
    print(data_raw)
    #
    # dataLine = data_raw.split(', ')
    # if not firstLine:
    #     rawPresFile.write(dataLine[0] + '\n')
    #     compPresFile.write(dataLine[1] + '\n')
    #     rawTempFile.write(dataLine[2] + '\n')
    #     compTempFile.write(dataLine[3] + '\n')
    #     rawHumFile.write(dataLine[4] + '\n')
    #     compHumFile.write(dataLine[5] + '\n')
    #     firstLine = True
    # else:
    #     rawPresFile.write(CompHumClass.HexValue_to_float(dataLine[0][4:]) + '\n')
    #     compPresFile.write(CompHumClass.HexValue_to_float(dataLine[1][2:]) + '\n')
    #     rawTempFile.write(CompHumClass.HexValue_to_float(dataLine[2][2:]) + '\n')
    #     compTempFile.write(CompHumClass.HexValue_to_float(dataLine[3][2:]) + '\n')
    #     rawHumFile.write(CompHumClass.HexValue_to_float(dataLine[4][2:]) + '\n')
    #     compHumFile.write(CompHumClass.HexValue_to_float(dataLine[5][2:8]) + '\n')

if debug:
    baroMsgsFile.close()

# rawPresFile.close()
# compPresFile.close()
# rawTempFile.close()
# compTempFile.close()
# rawHumFile.close()
# compHumFile.close()