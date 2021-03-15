import serial
from classes import CompHumClass
import time

rawPresFilePath = "data/RawPresLog.txt"
compPresFilePath = "data/CompPresLog.txt"
rawTempFilePath = "data/RawTempLog.txt"
compTempFilePath = "data/CompTempLog.txt"
rawHumFilePath = "data/RawHumLog.txt"
compHumFilePath = "data/CompTempLog.txt"

rawPresFile = open(rawPresFilePath, "w")
compPresFile = open(compPresFilePath, "w")
rawTempFile= open(rawTempFilePath, "w")
compTempFile = open(compTempFilePath, "w")
rawHumFile = open(rawHumFilePath, "w")
compHumFile = open(compHumFilePath, "w")

firstLine = False
ser = serial.Serial('/dev/ttyUSB0', 9600)
ser.flushInput()
ser.flushOutput()
while True:
    data_raw = str(ser.readline())
    print(data_raw)
    dataLine = data_raw.split(', ')
    if not firstLine:
        rawPresFile.write(dataLine[0] + '\n')
        compPresFile.write(dataLine[1]+ '\n')
        rawTempFile.write(dataLine[2] + '\n')
        compTempFile.write(dataLine[3] + '\n')
        rawHumFile.write(dataLine[4] + '\n')
        compHumFile.write(dataLine[5] + '\n')
        firstLine = True
    else:
        rawPresFile.write(CompHumClass.HexValue_to_float(dataLine[0][4:]) + '\n')
        compPresFile.write(CompHumClass.HexValue_to_float(dataLine[1][2:]) + '\n')
        rawTempFile.write(CompHumClass.HexValue_to_float(dataLine[2][2:]) + '\n')
        compTempFile.write(CompHumClass.HexValue_to_float(dataLine[3][2:]) + '\n')
        rawHumFile.write(CompHumClass.HexValue_to_float(dataLine[4][2:]) + '\n')
        compHumFile.write(CompHumClass.HexValue_to_float(dataLine[5][2:8]) + '\n')