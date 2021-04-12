import sys
import argparse
import multiprocessing as mp
from threading import *
from datetime import datetime
from importer import *
# from importer import receiver
from GUI import GUI_GO, presQueue, tempQueue, humQueue, altQueue, GPSQueue
from readUBX import *

import settings
from fakeserial import *
from fakeserial import receiver

import geojson


def getTimeStamp(arg):
    if arg:
        dateTimeObj = settings.fake_time
    else:
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


def start_gpx(file_obj):
    file_obj.write(
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        "<gpx\n"
        "  version=\"1.0\"\n"
        "  xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"\n"
        "  xmlns=\"http://www.topografix.com/GPX/1/0\"\n"
        "  xsi:schemaLocation=\"http://www.topografix.com/GPX/1/0 http://www.topografix.com/GPX/1/0/gpx.xsd\">\n"
        "\t<trk>\n"
        "\t\t<trkseg>\n"
    )


def write_gpx(file_obj, lat, lon, ele, time_str):
    file_obj.write("\t\t\t<trkpt lat=\"" + str(lat) + "\" lon=\"" + str(lon) + "\"><ele>" + str(ele) + "</ele><time>"
                   + time_str + "</time><name>" + time_str + "</name></trkpt>\n")


def end_gpx(file_obj):
    file_obj.write(
        "\t\t</trkseg>\n"
        "\t</trk>\n"
        "</gpx>"
    )

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

rawbarocsv = open("logs/decoded/rawbarodat.csv", 'w')
gpsgpx = open("logs/decoded/gpsmap.gpx", 'w')

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


def decodeLogData(data):
    # raw pressure decoding and logging
    rawPresHex = ""
    for i in range(0, 4):
        rawPresHex += data[i]
    rawPres = struct.unpack('<I', bytes.fromhex(rawPresHex))[0]
    print("Raw Pressure: " + str(rawPres))
    rawPresFile.write("Raw Pressure: " + str(rawPres) + "\n")
    dataFile.write("Raw Pressure: " + str(rawPres) + "\n")

    # Raw temp decoding and logging
    rawTempHex = ""
    for i in range(4, 8):
        rawTempHex += data[i]
    rawTemp = struct.unpack('<I', bytes.fromhex(rawTempHex))[0]
    print("Raw Temperature: " + str(rawTemp))
    rawTempFile.write("Raw Temperature: " + str(rawTemp) + "\n")
    dataFile.write("Raw Temperature: " + str(rawTemp) + "\n")

    # Raw humidity decoding and logging
    rawHumHex = ""
    for i in range(8, 12):
        rawHumHex += data[i]
    rawHum = struct.unpack('<I', bytes.fromhex(rawHumHex))[0]
    print("Raw Humidity: " + str(rawHum))
    rawHumFile.write("Raw Humidity: " + str(rawHum) + "\n")
    dataFile.write("Raw Humidity: " + str(rawHum) + "\n")

    # calculated pressure decode and logging
    calPresHex = ""
    for i in range(12, 16):
        calPresHex += data[i]
    calPres = struct.unpack('<f', bytes.fromhex(calPresHex))[0]
    print("Calculated Pressure(Pa): " + str(calPres))
    compPresFile.write(str(calPres) + "\n")
    dataFile.write("Calculated Pressure(Pa): " + str(calPres) + "\n")
    presQueue.put(calPres)

    # calculated tempurature decoding and logging
    calTempHex = ""
    for i in range(16, 20):
        calTempHex += data[i]
    calTemp = struct.unpack('<f', bytes.fromhex(calTempHex))[0]
    print("Calculated Temperature(C): " + str(calTemp))
    compTempFile.write(str(calTemp) + "\n")
    dataFile.write("Calculated Temperature(C): " + str(calTemp) + "\n")
    tempQueue.put(calTemp)

    # calculated humidity decoding and logging
    calHumHex = ""
    for i in range(20, 24):
        calHumHex += data[i]
    calHum = struct.unpack('<f', bytes.fromhex(calHumHex))[0]
    print("Calculated Humidity(%): " + str(calHum))
    compHumFile.write(str(calHum) + "\n")
    dataFile.write("Calculated Humidity(%): " + str(calHum) + "\n")
    humQueue.put(calHum)

    # calculated altitude decoding and logging
    calAltHex = ""
    for i in range(24, 28):
        calAltHex += data[i]
    calAlt = struct.unpack('<f', bytes.fromhex(calAltHex))[0]
    print("Calculated Altitude: " + str(calAlt))
    compAltFile.write(str(calAlt) + "\n")
    dataFile.write("Calculated Altitude(m): " + str(calAlt) + "\n")
    altQueue.put(calAlt)

    rawbarocsv.write(str(settings.msg_time) + ", " + str(rawPres) + ", " + str(rawTemp) + ", " + str(rawHum) + '\n')



print("*BEGINNING PROGRAM*\n\n")

dataFile.write("*BEGINNING PROGRAM*\n\n")
parser = argparse.ArgumentParser(description="Parse bool")
parser.add_argument("-D", '-development', default=False, action="store_true")
parser.add_argument("-G", '-GUI', default=False, action="store_true")

args = parser.parse_args()

if args.D:
    Fake = Thread(target=fakeserial, args=("test_data/HexFile_withtime.txt",))
    Fake.start()
else:
    importer = Thread(target=importSerial)
    importer.start()

if args.G:
    print("OPENING GUI")
    GUI = Thread(target=GUI_GO)
    GUI.start()


def main():

    state = "initial"
    baro_state = "payLoadLength"
    payLoadLenFlag = False
    payLoadLen = 0
    payLoadCount = 0
    dataCount = 0
    dataType_count = 1
    baroChecksumCount = 0
    data = []
    baroBytes = []
    gps_bytes = []
    gpsByte_string = ""
    baroChecksum = []
    GUI_iterater = 0
    time_arg = 0

    if args.D:
        time_arg = 1

    if args.G:
        print("*ENTERING DEVELOPMENT MODE*\n")
        dataFile.write("*ENTERING DEVELOPMENT MODE*\n")
        # baroMsgsFile = open(baroMsgsFilePath, "r")
        print("READING FROM FILE\n")
        dataFile.write("READING FROM FILE\n")
    else:

        print("READING FROM SERIAL\n")
        dataFile.write("READING FROM SERIAL\n")

    start_gpx(gpsgpx)
    write_gpx(gpsgpx, 0.228990, 37.307772, 2004.94, "2007-01-01T00:00:26Z")
    write_gpx(gpsgpx, 0.241400, 37.317961, 3004.94, "2007-12-31T23:00:49Z")
    end_gpx(gpsgpx)
    gpsgpx.close()

    while True:
        data_raw = receiver.recv()
        recv_timestamp = getTimeStamp(time_arg)
        if len(data_raw) == 2:
            settings.msg_time = settings.fake_delta
            if data_raw == "BB" and state == "initial":  # First starting byte
                print(recv_timestamp)
                dataFile.write("\n" + recv_timestamp + "\n")
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
                    payLoadCount = payLoadCount + 1
                    if payLoadCount == payLoadLen:
                        print("PAYLOAD READ IN")
                        dataFile.write("END OF PAYLOAD\n")
                        baro_state = "barochecksum"
                        baroChecksumCount = 0
                        payLoadLen = 0
                        payLoadCount = 0
                elif baro_state == "payLoadLength":
                    payLoadLen = int(data_raw, 16)
                    print("Barometer payload length is " + str(payLoadLen) + " bytes")
                    dataFile.write("Barometer payload length is " + str(payLoadLen) + " bytes\n")
                    baro_state = "payload"
                elif baro_state == "barochecksum":
                    baroChecksumCount = baroChecksumCount + 1
                    baroChecksum.append(data_raw)
                    if baroChecksumCount == 2:
                        if validateBaroChecksum(baroBytes, baroChecksum):
                            decodeLogData(baroBytes)
                        else:
                            print("CHECKSUM INVALID IGNORING DATA")
                        print("\n")
                        state = "initial"
                        data = []
                        baroBytes = []
                        baroChecksum = []
                        baro_state = "payLoadLength"
            elif state == "messageClass":
                if payLoadLenFlag:
                    # message data conversion

                    payLoadCount = payLoadCount + 1
                    if payLoadCount == payLoadLen:
                        print("END OF PAYLOAD")
                        dataFile.write("END OF PAYLOAD\n")
                        payLoadCount = 0
                else:
                    payLoadLen = int(data_raw, 16)
                    print("Message payload length is " + str(payLoadLen) + " bytes")
                    dataFile.write("Message payload length is " + str(payLoadLen) + " bytes\n")
                    baroBytes.append(data_raw)
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
                    "ERROR: missing starting flag, discarding incoming data(" + str(
                        data_raw) + ") and waiting till next start flags\n")
        else:
            continue


try:
    main()
except KeyboardInterrupt:
    # Importer.join()
    if args.D:
        Fake.join()
    if args.G:
        GUI.join()
    rawPresFile.close()
    compPresFile.close()
    rawTempFile.close()
    compTempFile.close()
    rawHumFile.close()
    compHumFile.close()
    dataFile.close()
    rawbarocsv.close()

    sys.exit(0)
