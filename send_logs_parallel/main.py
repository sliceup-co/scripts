import sys
from os import listdir
from os.path import isfile, join
import os
import re
import random
import time
import subprocess


if __name__ == "__main__":
    if (len(sys.argv) != 4):
        raise Exception("Please provide a directory for the log files and a target file")
    
    logs_dir = sys.argv[1]
    target_file = sys.argv[2]
    messages_per_second = float(sys.argv[3])
    rate = (1 / messages_per_second) / 2.0

    print(logs_dir, target_file, rate)


    onlyfiles = [f for f in listdir(logs_dir) if isfile(join(logs_dir, f))]
    onlyfiles = [f for f in onlyfiles if ((len(f) > 4) and (f[-4:] == ".log"))]
    
    file_handlers = [open(join(logs_dir,filename), "r") for filename in onlyfiles]
    count = [0] * len(file_handlers)

    target_file_handler = open(target_file, "w+")

    count_line = 0
    while(len(file_handlers) > 0):
        count_line += 1
        if (count_line == 10000):
            count_line = 0
            print("Restarting tmp file")
            target_file_handler.close()
            target_file_handler = open(target_file, "w")
            os.system("systemctl restart rsyslog")

        idx = random.randint(0, len(file_handlers) - 1)
        try:
            a = next(file_handlers[idx])
            target_file_handler.write(a)
            count[idx] += 1
            time.sleep(rate)
        except:
            print("Removing {} ({})".format(onlyfiles[idx], count[idx]))
            file_handlers.pop(idx)
            count.pop(idx)