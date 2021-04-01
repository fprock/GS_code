from queue import *
import multiprocessing as mp
from time import sleep

def testingRead():
    test = Queue()
    global b
    a, b = mp.Pipe()
    hexFile = open('Testdata.txt', "r")
    i = 0
    Importer = mp.Process(target=testingWrite)
    Importer.start()
    while True:
        data = hexFile.read(2)
        a.send(data)


def testingWrite():
    sleep(5)
    while True:
        data = b.recv()
        print(str(len(data)))
        break


testingRead()
