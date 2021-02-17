# "bluetooth" Stadia controller
There are a lot of caveats to go over here. Please read the entire readme before starting to use this.
!["wireless bluetooth"](final.jpeg)

## Requirements
This program only currently works only RPi0W to other Linux based machines, but if any
- RPi0W or similar device with **bluetooth** capabilities.
- Battery bank
- Cables
    + from battery bank to RPi0W (typically USB A to micro B)
    + A micro B to full size USB A hub
    + A USB A to USB C
- Free time (a lot of it!)
- Basic linux/python knowledge.

## Installation
### On RPi0W
Assuming that you have a basic setup with ssh going;
- Install python bluetooth libraries
    + `pip3 install pybluez`
    + Assuming debian based system:
        * `sudo apt install libbluetooth3`
- Install `evtest`
    + `sudo apt install evtest`

Note that the process has changed to move the client side away from relying on the `python-evdev` module. Instead it uses pipes, evtest regex and stdin. Despite this seeming to increase the complexity of the project the latency has improved greatly.




### On game (linux) computer
Follow the steps above and the following additional steps to enable the `ptyhon-evdev` module.

`pip3 install evdev`

Add your user to the input group:

`sudo usermod -a -G input pi`

Then reboot. This should be all that you need to do.

If you don't want to bother with trouble shooting `input` access issues you can also install the `pip` packages as root and run the program as root.


## Usage
Start the server on your game computer;

`python3 btserver.py --cap stadia`

Make sure all the things are plugged in on your RPi0W

Start the client on your RPi0W; (assuming that the file are executable)

`./run | ./btstdinclient.py`

They should connect within about 30 seconds. 

You should be good to go!

## Run at boot on RPi0W
Use the new `stadia.service` file.

Note that it expects the following files in the `/home/pi` directory.

- `/home/pi/run`
- `/home/pi/btstdinclient.py`
- `/home/pi/wrapper`

This is because `systemd` is very stupid and a pain in the ass. It is just easier to use pipes inside of a wrapper file than directly in the `systemd` service file. It is necessary to use because it is configured to only start the program after bluetooth is ready. 

Even with the `systemd` waiting for bluetooth, it seems (for me) to be necessary to have another delay. This is accomplished in the `wrapper` file with the second line `sleep 10`. Feel free to try and tweak to get better timings.

## How can I see what my lag is?
Well this turns out to be a pretty complicated question.

There is not really an easy way to determine if computer clocks are on the exact same time, which makes it an issue trying to determine the time differences. Depending on setup/randomness you can get "negative" lag as measured by the below methods.

`evtest /path/to/input >> events`

On both the remote and local system, then run them through `python3 eventprocessor.py <filename>` which will output the data in a CSV format. Which you can then compare. 

I might upload some graphs for the new lag stats but they are much improved with the piping system. The lag also does not seem to be at all effected by the use of the analog inputs on the controller.


## Limitations
Currently only supports Linux as the remote device. I've been looking around for a input emulation library for windows but none seem to be actively maintained. If you have any suggestions open an issue with a link to the library and I'll look into it. 

Feel free to open a PR if you get something working.

Bluetooth struggles connecting. Not sure if there is even anything to be done about that or if it is just BT being BT.

Lag! It's not zero latency. Not sure what you want. Go bug Google to flip a switch and enable bluetooth functionality on the controllers. 

My RPi0W can't seem to detect that the Stadia controller has rumble so that feature is going to be completely absent. 

There are `EV_MSC` (miscellaneous) events that aren't being properly translated. These don't appear to effect anything as far as I can tell. The issue is with the `json.loads` not handling hex values. A fix is difficult to implement because the other `value`s are not hex. As always feel free to open a PR.

## TODO
* Windows support as detailed below
* MacOS support too cause why not its just a TODO
* Enable all `EV_MSC` commands to be sent.
* BTHID. This would in theory solve the crossplatform issues.


## Windows still needs to be implemented
Fuck developing on windows man. I tried for just way to long to get just `pybluez` installed. This is mostly because I have been greatly spoiled by using Linux and it's package management system.

Any way if you are enterprising enough to make an attempt here is a general outline of how I was planning on implementation.

* The client will remain unchanged.
* The server code can mostly be directly copied over;
    - just have to modify the `ui.write` command in the main `while` loop to use some kind of map to translate `evdev` codes to whatever codes are used by the windows library.
    - vJoy seems to be pretty promising in my initial search. Sketchy install tho, good ole sourceforge `.exe` download.


While it is exciting to bring support for this system to other platforms I don't recommend it. Windows is quite the pain in the ass with python bluetooth. Windows is just terrible in general please don't use it for anything.

* Install vjoy
http://vjoystick.sourceforge.net/site/index.php/download-a-install/download

* Install vsbuild tools (`Visual C++ 14.0`)

You have to go to [this](https://visualstudio.microsoft.com/downloads/) page and scroll down, click the search bar and type in "build tools". 



* Install pip packages used;
    - wheel
    - pyvjoy
* Make sure that pip is fully upgraded

