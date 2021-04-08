from datetime import datetime, timedelta
from multiprocessing import Pipe
import time

global receiver
sender, receiver = Pipe()


def fakeserial(input_file_path):

    data_timestamp = []
    data_bytes = []
    data_seconds = []
    strtend_file = open("logs/start_end.txt", 'w')
    input_file = open(input_file_path, 'r')
    all_lines = input_file.readlines()
    for i in range(0, len(all_lines)):
        #                                   03-Apr-2021 (15:43:29.812437):
        data_timestamp.append(datetime.strptime(str(all_lines[i])[0:30], '%d-%b-%Y (%H:%M:%S.%f):'))
        data_bytes.append(str(all_lines[i])[31:33])

        # data_seconds.append(timedelta(hours=data_timestamp[i].hour, minutes=data_timestamp[i].minute, seconds=data_timestamp[i].second, microseconds=data_timestamp[i].microsecond).total_seconds())
        data_seconds.append(
            timedelta(hours=data_timestamp[i].hour, minutes=data_timestamp[i].minute, seconds=data_timestamp[i].second,
                      microseconds=data_timestamp[i].microsecond).total_seconds())

    real_full_delta = data_seconds[-1] - data_seconds[0]
    x = 0
    dateTimeObjStart = datetime.now()
    timestampStart = dateTimeObjStart.strftime("%d-%b-%Y (%H:%M:%S.%f)")
    print("Start Time: " + timestampStart + '\n')
    strtend_file.write("Start Time: " + timestampStart + '\n')
    new_delta_start = timedelta(hours=dateTimeObjStart.hour, minutes=dateTimeObjStart.minute, seconds=dateTimeObjStart.second,
                  microseconds=dateTimeObjStart.microsecond).total_seconds()

    while x < len(data_seconds) - 1:
        # print("while\n")
        sender.send(str(data_bytes[x]))
        sleep_dur = float(data_seconds[x + 1]) - float(data_seconds[x])
        x += 1
        time.sleep(sleep_dur)

    dateTimeObjEnd = datetime.now()
    timestampEnd = dateTimeObjEnd.strftime("%d-%b-%Y (%H:%M:%S.%f)")
    new_delta_end = timedelta(hours=dateTimeObjEnd.hour, minutes=dateTimeObjEnd.minute,
                                seconds=dateTimeObjEnd.second,
                                microseconds=dateTimeObjEnd.microsecond).total_seconds()

    new_delta = new_delta_end - new_delta_start
    print("End Time: " + timestampEnd + '\n')
    strtend_file.write("End Time: " + timestampEnd + '\n')
    # delta = dateTimeObjStart.timedelta(hours=dateTimeObjEnd.hour, minutes=dateTimeObjEnd.minute, seconds=dateTimeObjEnd.second, microseconds=dateTimeObjEnd.microsecond)
    print(str(new_delta) + '\n')
    strtend_file.write("new delta:" + str(new_delta) + '\n')
    strtend_file.write("real delta:" + str(real_full_delta) + '\n')



if __name__ == '__main__':
    fakeserial("logs/raw/HexFile_withtime.txt")