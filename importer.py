import serial
import queue
import sys
import time
import argparse
import struct
from datetime import datetime
from readUBX import *
import pprint
import threading
import queue
import variables




def importSerial():
    variables.init()
    ser = serial.Serial('/dev/ttyUSB0', 9600)
    ser.flushInput()
    ser.flushOutput()
    byteFile = open("logs/ByteFile.txt", 'w')
    hexFile = open("logs/HexFile.txt", 'w')

    while True:
        while ser.in_waiting:
            byte = ser.read(1)
            byteFile.write(str(byte) + '\n')
            hex = str(byte)[4:6]
            if hex == "":
                continue
            elif hex == "\n":
                continue
            elif hex == "'":
                continue
            hex = hex.upper()
            print(hex)
            hexFile.write(hex)
        if not ser.in_waiting:
            variables.hexBytes.put(1)

