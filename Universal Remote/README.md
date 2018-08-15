# Universal Remote Control
## Overview
This implementation uses LIRC - Linux Infrared Remote Control.
A basic circuit is needed to allow LIRC to use the Raspberry Pi's ports to flash the correct LED codes.

![Basic IR Circuit](/Doc/kydhome_img/IR-LED.png)

This [Link](http://www.raspberry-pi-geek.com/Archive/2015/10/Raspberry-Pi-IR-remote) describes the process of installing and configuring the software  and the hardware.

## Process For Installation
This process assumes you have the Raspberry Pi setup with Rasbian.

The ouput pin for the IR transmitter is GPIO22
The input pin for the IR transmitter is GPIO23
![RPI GPIO](/Doc/kydhome_img/Raspberry-Pi-GPIO-Layout-Model-B-Plus.png)
1. First run **sudo apt-get install lirc** - this installs the lirc kernel module.
2. Add the following lines to /etc/modules file:
*lirc_dev
lirc_rpi gpio_in_pin=23 gpio_out_pin=22*
