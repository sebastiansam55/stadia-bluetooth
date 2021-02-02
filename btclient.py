import bluetooth
from bluetooth import BluetoothError
import argparse
import os
import time
import sys
import evdev
from evdev import ff, ecodes as e

parser = argparse.ArgumentParser(description="UInput forwarding over bluetooth")
parser.add_argument('-u', '--uuid', dest="uuid", default="1111", action="store", help="UUID of remate service")
parser.add_argument('-d', '--device_desc', dest="device_desc", action="store", default="Google Inc. Stadia Controller", help="Name of device to grab")
parser.add_argument('-v', '--verbose', dest="verbose", action="store_true", help="Verbose logging")
parser.add_argument('--debug', dest="debug", default=False, action="store_true", help="Enable client debug (will not write events)")
parser.add_argument('--default', dest="default", action="store", default="null", help="Default client to send events to")

args = parser.parse_args()

def get_devices():
    return [evdev.InputDevice(path) for path in evdev.list_devices()]

def grab_device(devices, descriptor):
    #determine if descriptor is a path or a name
    return_device = None
    if "/dev/" in descriptor: #assume function was passed a path
        for device in devices:
            if descriptor==device.path:
                device.close()
                return_device = evdev.InputDevice(device.path)
            else:
                device.close()
    else: #assume that function was passed a plain text name
        for device in devices:
            if descriptor==device.name:
                device.close()
                return_device = evdev.InputDevice(device.path)
            else:
                device.close()
    return return_device

def get_dev():
    devices = get_devices()
    print("Attempting grab: ", args.device_desc)
    device = grab_device(devices, args.device_desc)
    if device:
        print("Device captured: ", args.device_desc)
        return device

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

# def rumble(device):
#     #rumble on connect
#     rumble = ff.Rumble(strong_magnitude=0x0000, weak_magnitude=0xffff)
#     effect_type = ff.EffectType(ff_rumble_effect=rumble)
#     duration_ms = 1000

#     effect = ff.Effect(
#         e.FF_RUMBLE, -1, 0,
#         ff.Trigger(0, 0),
#         ff.Replay(duration_ms, 0),
#         ff.EffectType(ff_rumble_effect=rumble)
#     )

#     repeat_count = 1
#     effect_id = device.upload_effect(effect)
#     device.write(e.EV_FF, effect_id, repeat_count)
#     device.erase_effect(effect_id)

#first run init
sock = None
while sock is None:
    sock = connect()
    time.sleep(1)
device = None
while device is None:
    device = get_dev()
    time.sleep(1)


#doesnt appear to be supported on rpi0? Needs further investigation.
# rumble(device)



while True:
    try:
        for ev in device.read_loop():
            ts = ev.timestamp()
            if time.time()>ts+1: #forget events over 1s old
                continue
            data = {
                "timestamp": str(ts),
                "type": ev.type,
                "code": ev.code,
                "value": ev.value,
                "sendto": args.default
            }
            try:
                ret = sock.send(str(data))
            except BluetoothError:
                print("Device disconnect; BluetoothError")
                sock = None
                while sock is None:
                    sock = connect()
                    time.sleep(1)
    except OSError:
        print("Device error, or device disconnect")
        device = None
        while device is None:
            device = get_dev()
            time.sleep(1)

sock.close()