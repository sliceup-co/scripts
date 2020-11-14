import sys
from os import listdir
from os.path import isfile, join
import os
import re
import random
import time
import subprocess
import socket
import sys
import argparse 
from datetime import datetime
import numpy as np
import logging

logFormatter = '%(asctime)s - %(pid)s - %(user)s - %(levelname)s - %(message)s'
logging.basicConfig(format=logFormatter, level=logging.DEBUG)
logger = logging.getLogger(__name__)

def log(message):
    logger.info(message, extra={'user': 'sliceup-log-sender', 'pid': os.getpid()})



class Handler:
    BASE_MESSAGE = '<14>1 {} {} Rhttpproxy - - [00Originator@6876 loc="cdeww" fwd="cdeww" vcenter="cdeww" imp="infra" lmp="infra"] {}'    

    def __init__(self, n, dst, messages_per_second, hostname, debug_every = 10000, max_message_length = 999999):
        self.n = n
        self.hostnames, self.host_dist = self.get_hosts(hostname)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.dst = dst
        self.sock.connect(dst)
        log("Established connection with {}".format(dst))
        self.messages_per_second = messages_per_second
        self.messages_sent = 0
        self.global_messages_sent = 0
        self.truncated = 0
        self.last_update = datetime.now()
        self.back_off_time = 1
        self.debug_every = debug_every
        self.max_message_length = max_message_length

    def get_now(self):
        return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.0Z")

    def get_hosts(self, prefix):
        n = self.n
        hostnames = ["{}-{}".format(prefix, i + 1) for i in range(n)]
        dist = np.random.uniform(0, n, n)
        dist = dist / dist.sum()

        return hostnames, dist

    def get_host(self):
        return self.hostnames[np.random.choice(self.n, p=self.host_dist)]

    def get_syslog_message(self, message):
        if (len(message) > self.max_message_length):
            message = message[:self.max_message_length] + message[-1]
            self.truncated += 1

        return Handler.BASE_MESSAGE.format(self.get_now(), self.get_host(), message)

    def send_syslog_message(self, message, files_open):
        mes = self.get_syslog_message(message)
        while (True):
            try:
                self.sock.sendall(bytes(mes, "UTF-8"))
                break
            except Exception as e:
                self.sock.close()
                time.sleep(self.back_off_time)
                self.back_off_time = min(60, self.back_off_time * 2)
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect(self.dst)
                self.back_off_time

        self.messages_sent += 1

        self.global_messages_sent += 1
        if (self.global_messages_sent == self.debug_every):
            log("sent {} messages ({} truncated) with {} files open".format(self.debug_every, self.truncated, files_open))
            self.global_messages_sent = 0


        if (self.messages_sent == self.messages_per_second):
            now = datetime.now()
            diff = now - self.last_update 
            diff = diff.seconds + diff.microseconds / 1000000
            sleep_time = max(0, 1 - diff)
            time.sleep(sleep_time)
            self.last_update = datetime.now()
            self.messages_sent = 0



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Send messages from logs in parallel')
    
    parser.add_argument('--loc', help='A location for the logs to be sent')
    parser.add_argument('--loop', help='A boolean to determine if to loop forever or not')
    parser.add_argument('--dst', help='The ip and port of the destination')
    parser.add_argument('--rate', help='The rate of logs per second to be sent')
    parser.add_argument('--hosts', help='The number of virtual logs')
    parser.add_argument('--hostname', help='The name that the host will take.')
    parser.add_argument('--debug', help='After how many messages will the program log.')
    parser.add_argument('--max-message-length', help='The maximun length a log line can have.')


    args = parser.parse_args()

    if ((args.loc == None) or (args.loop == None) or (args.dst == None) or \
        (args.rate == None) or (args.hosts == None) or (args.hostname == None)):
        raise Exception("Please provide all the necessary arguments. Run 'python main.py --help'")
    
    LOGS_DIR = args.loc
    SLEEP_TIME = 1.0 / float(args.rate)
    LOOP = True if args.loop.lower() == "true" else False
    DSTS = [ (dst.split(":")[0], int(dst.split(":")[1])) for dst in args.dst.split(",") ]
    HOSTS_N = int(args.hosts)
    HOSTNAME = args.hostname
    DEBUG_EVERY = int(args.debug)
    MAX_MESSAGE_LENGTH = int(args.max_message_length)

    handlers = [Handler(HOSTS_N, DST, int(args.rate), HOSTNAME, debug_every=DEBUG_EVERY, max_message_length=MAX_MESSAGE_LENGTH) for DST in DSTS]
    
    
    while(True):
        onlyfiles_reserve = [f for f in listdir(LOGS_DIR) if isfile(join(LOGS_DIR, f))]
        onlyfiles_reserve = [f for f in onlyfiles_reserve if ((len(f) > 4) and (f[-4:] == ".log"))]

        RESERVE_SIZE = 400
        while (len(onlyfiles_reserve) > 0):

            if (len(onlyfiles_reserve) > RESERVE_SIZE):
                onlyfiles = onlyfiles_reserve[:RESERVE_SIZE]
                onlyfiles_reserve = onlyfiles_reserve[RESERVE_SIZE:]
            else:
                onlyfiles = onlyfiles_reserve[:]
                onlyfiles_reserve = onlyfiles_reserve[len(onlyfiles_reserve):]
            
            file_handlers = [open(join(LOGS_DIR,filename), "r") for filename in onlyfiles]
            count = [0] * len(file_handlers)

            while(len(file_handlers) > 0):
                idx = random.randint(0, len(file_handlers) - 1)
                try:
                    a = next(file_handlers[idx])
                    try:
                        [handler.send_syslog_message(a, len(file_handlers)) for handler in handlers]
                    except Exception as e:
                        print(e)
                    count[idx] += 1
                except KeyboardInterrupt:
                    sys.exit()
        
                except:
                    #log("Removing {} ({})".format(onlyfiles[idx], count[idx]))
                    file_handlers.pop(idx)
                    count.pop(idx)

                    onlyfiles_reserve.append(onlyfiles.pop(idx))                    
                   
                    new_file_idx = random.randint(0, len(onlyfiles_reserve) - 2)
                    new_file = onlyfiles_reserve[new_file_idx]
                    onlyfiles.append(onlyfiles_reserve.pop(new_file_idx))
                    file_handlers.append(open(join(LOGS_DIR,new_file), "r"))
                    count.append(0)


        
        if (not LOOP):
            break
        print("Starting another round ...")
    log("exiting...")
