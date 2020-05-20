import sys
from os import listdir
from os.path import isfile, join
import os
import re
import random
import time
import subprocess


if __name__ == "__main__":
    if (len(sys.argv) != 2):
        raise Exception("Please provide a directory for the log files and a target file")
    
    logs_dir = "mounted_logs"
    messages_per_second = float(sys.argv[1])
    rate = (1 / messages_per_second) / 2.0


    onlyfiles = [f for f in listdir(logs_dir) if isfile(join(logs_dir, f))]
    onlyfiles = [f for f in onlyfiles if ((len(f) > 4) and (f[-4:] == ".log"))]
    
    file_handlers = [open(join(logs_dir,filename), "r") for filename in onlyfiles]
    count = [0] * len(file_handlers)

    global_counter = 0
    while(len(file_handlers) > 0):
        global_counter += 1
        if (global_counter % 10000 == 0):
            print(global_counter)

        idx = random.randint(0, len(file_handlers) - 1)
        try:
            a = next(file_handlers[idx])
            print(a[:-1] + "(" + str(global_counter) + ")")
            count[idx] += 1
            time.sleep(rate)
        except KeyboardInterrupt:
            sys.exit()
 
        except:
            print("Removing {} ({})".format(onlyfiles[idx], count[idx]))
            file_handlers.pop(idx)
            count.pop(idx)

