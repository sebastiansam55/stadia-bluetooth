import bluetooth
from bluetooth import BluetoothError
import json
import time
import argparse
import evdev
from evdev import AbsInfo, ecodes as e

parser = argparse.ArgumentParser(description="UInput forwarding over bluetooth")
parser.add_argument('-u', '--uuid', dest="uuid", default="1111", action="store", help="UUID of remate service")
parser.add_argument('-d', '--dev_name', dest="dev_name", default="Google Inc. Stadia Controller", action="store", help="Name of device to be created for remote interactions")
parser.add_argument('--debug', dest="debug", default=False, action="store_true", help="Enable client debug (will not write events)")
parser.add_argument('--cap', dest="cap", default="mouse keyboard", action="store", help="Description of device to be created for input. [keyboard, mouse, trackpad, stadia]")
parser.add_argument('--all', dest="exec_all", default=False, action="store_true", help="Execute all recieved commands")

args = parser.parse_args()

def get_cap(dd):
    cap = {}
    if dd:
        print(dd)
        ddl = dd.split(" ")
        for item in ddl:
            if item == "keyboard":
                cap[e.EV_KEY] = e.keys.keys()
            elif item == "mouse":
                cap[e.EV_REL] = [
                    e.REL_X,
                    e.REL_Y,
                    e.REL_HWHEEL,
                    e.REL_WHEEL,
                    e.REL_HWHEEL_HI_RES,
                    e.REL_WHEEL_HI_RES
                ]
            elif item == "stadia":
                cap[e.EV_KEY] = [
                    e.BTN_SOUTH,
                    e.BTN_EAST,
                    e.BTN_NORTH,
                    e.BTN_WEST,
                    e.BTN_TL,
                    e.BTN_TR,
                    e.BTN_SELECT,
                    e.BTN_START,
                    e.BTN_MODE,
                    e.BTN_THUMBL,
                    e.BTN_THUMBR,
                    e.BTN_TRIGGER_HAPPY1,
                    e.BTN_TRIGGER_HAPPY2,
                    e.BTN_TRIGGER_HAPPY3,
                    e.BTN_TRIGGER_HAPPY4
                ]
                cap[e.EV_ABS] = [
                    (e.ABS_X,     AbsInfo(value=128, min=1, max=255, fuzz=0, flat=15, resolution=0)),
                    (e.ABS_Y,     AbsInfo(value=128, min=1, max=255, fuzz=0, flat=15, resolution=0)),
                    (e.ABS_Z,     AbsInfo(value=128, min=1, max=255, fuzz=0, flat=15, resolution=0)),
                    (e.ABS_RZ,    AbsInfo(value=128, min=1, max=255, fuzz=0, flat=15, resolution=0)),
                    (e.ABS_GAS,   AbsInfo(value=0, min=0, max=255, fuzz=0, flat=15, resolution=0)),
                    (e.ABS_BRAKE, AbsInfo(value=0, min=0, max=255, fuzz=0, flat=15, resolution=0)),
                    (e.ABS_HAT0X, AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0)),
                    (e.ABS_HAT0Y, AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0))
                ]
                cap[e.EV_MSC] = [
                    e.MSC_SCAN
                ]

                pass
    return cap


def advert(server_socket):
    port = server_socket.getsockname()[1]

    bluetooth.advertise_service(server_socket, "UInput KVM", service_id=args.uuid,
                                service_classes=[args.uuid, bluetooth.SERIAL_PORT_CLASS],
                                profiles=[bluetooth.SERIAL_PORT_PROFILE],
                                )

    print("Waiting for connection on RFCOMM port", port)

    client_sock, client_info = server_socket.accept()
    print("Accepted connection from", client_info)
    return client_sock

def build_server():
    #init server
    server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM) #RFCOMM is apparently the only cross platform option
    server_socket.bind(("", bluetooth.PORT_ANY))
    server_socket.listen(1)
    return server_socket


ss = build_server()
cs = advert(ss)

print("Making uinput device:", args.dev_name)
ui = evdev.UInput(get_cap(args.cap), name=args.dev_name, vendor=0x18d1, product=0x9400, version=0x111)

while True:
    try:
        msg = cs.recv(1024).decode("utf-8")
        if not msg:
            break
        try:
            data = json.loads(msg.replace("'", "\""))
        except:
            print("JSON ERROR")
            continue
        # print(time.time()-float(data['timestamp']))
        if not args.debug:
            ui.write(data["type"], data["code"], data["value"])
        else:
            if not args.quiet: print("Write event:", data["type"], data["code"], data["value"])
    except BluetoothError:
        print("Bluetooth error, relaunching server")
        cs.close()
        ss.close()
        ss = build_server()
        cs = None
        while cs == None:
            cs = advert(ss)




print("Disconnected.")

client_sock.close()
server_socket.close()
print("All done.")