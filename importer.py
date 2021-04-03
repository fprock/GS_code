import serial
from multiprocessing import Pipe
from codecs import *
from datetime import *
global receiver
sender, receiver = Pipe()


def importSerial(SerOrLog):
    if not SerOrLog:
        ser = serial.Serial('/dev/ttyUSB0', 9600)
        ser.flushInput()
        ser.flushOutput()

    byteFile = open("logs/raw/ByteFile.txt", 'w')
    hexFileT = open("logs/raw/HexFile_withtime.txt", 'w')
    dataFile = open("Testdata.txt", "r")

    while True:
        if SerOrLog:
            data = dataFile.read(2)
            sender.send(data)
        else:
            while ser.in_waiting:
                byte = ser.read(1)
                byteFile.write(str(byte))
                data = byte.hex()
                data = data.upper()
                dateTimeObj = datetime.now()
                timestampStr = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S.%f)")
                hexFileT.write(timestampStr + ": " + data + "\n")
                sender.send(data)
            if not ser.in_waiting:
                item = ""
                sender.send(item)

