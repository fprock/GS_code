import serial
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

ser = serial.Serial('/dev/ttyUSB0', 9600)
ser.flushInput()
ser.flushOutput()
while True:
    data_raw = str(ser.readline())
    print(data_raw)
    dataline = data_raw.split(', ')
    rawPresFile.write(dataline[0] + '\n')
    compPresFile.write(dataline[1] + '\n')
    rawTempFile.write(dataline[2] + '\n')
    compTempFile.write(dataline[3] + '\n')
    rawHumFile.write(dataline[4] + '\n')
    compHumFile.write(dataline[5] + '\n')