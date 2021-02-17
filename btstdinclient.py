#!/usr/bin/python3

import bluetooth
from bluetooth import BluetoothError
import os
import time
import sys
import argparse
import fileinput
import re

parser = argparse.ArgumentParser(description="UInput forwarding over bluetooth. Connects to RFCOMM with uuid of 1111 by default")
parser.add_argument('-u', '--uuid', dest="uuid", default="1111", action="store", help="UUID of remote service")

args = parser.parse_args()

def connect():
    print("Trying connect")
    service_matches = bluetooth.find_service(uuid=args.uuid, address=None) # set as none to scan?

    if len(service_matches) == 0:
        print("Couldn't find the UInput KVM service.")
        return None
        # time.sleep(5)

    #go with the first match
    first_match = service_matches[0]
    port = first_match["port"]
    name = first_match["name"]
    host = first_match["host"]

    print("Found server at:", port, name, host)

    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((host, port))

    return sock

#first run init
sock = None
while sock is None:
    sock = connect()
    time.sleep(1)

data = ""
for line in fileinput.input():
    line = line.strip()
    if "SYN_REPORT" in line and data!="":
        try:
            # print(data)
            ret = sock.send(data)
            data = ""
        except BluetoothError:
            print("Device disconnect; BluetoothError")
            sock = None
            while sock is None:
                sock = connect()
                time.sleep(1)
    else:
        try:
            mat = re.findall(r'type (.*?) .*?, code (.*?) .*?, value (.*?)$', line)[0]
            # print(int(mat[2], 16))
            data += '{"type":'+mat[0]+',"code":'+mat[1]+',"value":'+mat[2]+'}'
        except:
            pass
    

sock.close()

