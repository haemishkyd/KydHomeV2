# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
import gc
import webrepl
import network

def do_connect():
    connected = False
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)

    if (sta_if.isconnected()):
        connected = True

    if (connected == False):
        print("Trying TP-LINK_6F7BD8")
        sta_if.connect('TP-LINK_6F7BD8', '12878536')
        while not sta_if.isconnected():
            pass

    if (sta_if.isconnected()):
        connected = True
        print('network config:', sta_if.ifconfig())
        ap_if = network.WLAN(network.AP_IF)
        ap_if.active(True)
        ap_if.config(essid='PoolPumpESP')

    return connected    


while (do_connect() != True):
    pass
webrepl.start()
gc.collect()
