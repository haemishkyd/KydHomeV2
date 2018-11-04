# Universal Remote Control
## Overview
This implementation uses LIRC - Linux Infrared Remote Control.
A basic circuit is needed to allow LIRC to use the Raspberry Pi's ports to flash the correct LED codes.

![Basic IR Circuit](/Doc/kydhome_img/IR-LED.png)

## Process For Installation
This process assumes you have the Raspberry Pi setup with Rasbian.

<img src="/Doc/kydhome_img/Raspberry-Pi-GPIO-Layout-Model-B-Plus.png" width="200">

The ouput pin for the IR transmitter is GPIO22<br>
The input pin for the IR transmitter is GPIO23<br>


1. First run **sudo apt-get install lirc** - this installs the lirc kernel module.
2. Add the following lines to /etc/modules file:<br>
*lirc_dev<br>
lirc_rpi gpio_in_pin=23 gpio_out_pin=22*
3. Add the following lines to /etc/lirc/hardware.conf file:<br>
*LIRCD_ARGS="--uinput --listen"<br>
LOAD_MODULES=true<br>
DRIVER="default"<br>
DEVICE="/dev/lirc0"<br>
MODULES="lirc_rpi"*
**Just make this file if it doesn't exist.**
4. Update the following line in /boot/config.txt:<br>
*dtoverlay=lirc-rpi,gpio_in_pin=23,gpio_out_pin=22*
5. Update the following lines in /etc/lirc/lirc_options.conf:<br>
*driver    = default<br>
device    = /dev/lirc0*

sudo /etc/init.d/lircd stop<br>
sudo /etc/init.d/lircd start<br>
These two commands will stop and start the lirc kernel module respectively.<br>

This information is sourced from this [link](https://gist.github.com/prasanthj/c15a5298eb682bde34961c322c95378b)<br>
This [link](http://www.raspberry-pi-geek.com/Archive/2015/10/Raspberry-Pi-IR-remote) also describes *some* of the process of installing and configuring the software  and the hardware.<br>

The package **mgp123** needs to also be installed. *sudo apt-get install mpg123*<br>
The python package **mqtt-paho** needs to be installed. *pip3 install paho-mqtt*<br>
The python packahe **gtts** needs to be installed. *pip3 install gtts*
Make the directory **~/sound_files** - this is where the script stores the generated mp3 files.

Store the service file in /lib/systemd/system. Thereafter run *systemctl enable universal_remote.service*

The volume of the Raspberry Pi might need to be changed. This [link](http://raspberrypi-aa.github.io/session3/audio.html) explains how to do this.

