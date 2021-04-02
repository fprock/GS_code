import serial
from multiprocessing import Pipe
from codecs import *

global receiver
sender, receiver = Pipe()


def importSerial(SerOrLog):
    ser = serial.Serial('/dev/ttyUSB0', 9600)
    ser.flushInput()
    ser.flushOutput()
    byteFile = open("logs/ByteFile.txt", 'w')
    hexFile = open("logs/HexFile.txt", 'w')
    dataFile = open("Testdata.txt", "r")

    while True:
        if SerOrLog:
            data = dataFile.read(2)
            sender.send(data)
        else:
            while ser.in_waiting:
                byte = ser.read(1)
                byteFile.write(str(byte.hex()) + '\n')
                data = byte.hex()
                data = data.upper()
                hexFile.write(data)
                sender.send(data)
            if not ser.in_waiting:
                item = ""
                sender.send(item)

