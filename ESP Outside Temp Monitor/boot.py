# This file is executed on every boot (including wake-boot from deepsleep)
import esp
esp.osdebug(None)
import gc
import webrepl
import time
import network 


def get_current_milliseconds():
    return time.ticks_ms()


def do_connect():
    connected = False
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)

    if (sta_if.isconnected()):
        connected = True

    if (connected == False):
        print("Trying NETGEAR41")
        sta_if.connect('NETGEAR41', 'xxxxxxxx')
        while not sta_if.isconnected():
            pass

    if (sta_if.isconnected()):
        connected = True
        print('network config:', sta_if.ifconfig())
        ap_if = network.WLAN(network.AP_IF)
        ap_if.active(True)
        ap_if.config(essid='OutsideTempESP')

    return connected


while (do_connect() != True):
    pass
webrepl.start()
gc.collect()
