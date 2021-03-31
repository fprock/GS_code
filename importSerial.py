import serial
import sys
import time
import argparse
import struct
from datetime import datetime
from readUBX import *
import pprint
import threading


ser = serial.Serial('/dev/ttyUSB0', 9600)
ser.flushInput()
ser.flushOutput()
byteFile = open("ByteFile.txt", 'w')
hexFile = open("HexFile.txt", 'w') 

while True:
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
        