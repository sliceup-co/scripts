import sys
from os import listdir
from os.path import isfile, join
import os
import re
import random
import time
import subprocess


if __name__ == "__main__":
    if (len(sys.argv) != 2) and (len(sys.argv) != 3):
        raise Exception("Please provide a directory for the log files and a target file")
    
    logs_dir = "mounted_logs"
    messages_per_second = float(sys.argv[1])
    rate = (1 / messages_per_second) / 2.0
    if (len(sys.argv) == 3) and (sys.argv[2].lower() == "true"):
        loop_forever = True
    else:
        loop_forever = False
    
    while(True):
        onlyfiles_reserve = [f for f in listdir(logs_dir) if isfile(join(logs_dir, f))]
        onlyfiles_reserve = [f for f in onlyfiles_reserve if ((len(f) > 4) and (f[-4:] == ".log"))]
        while (len(onlyfiles_reserve) > 0):

            if (len(onlyfiles_reserve) > 10):
                onlyfiles = onlyfiles_reserve[:10]
                onlyfiles_reserve = onlyfiles_reserve[10:]
            else:
                onlyfiles = onlyfiles_reserve[:]
                onlyfiles_reserve = onlyfiles_reserve[len(onlyfiles_reserve):]
            
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
            print("Starting another round ...")
        
        if (not loop_forever):
            break

