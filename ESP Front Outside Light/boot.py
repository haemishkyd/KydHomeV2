# This file is executed on every boot (including wake-boot from deepsleep)
import esp
esp.osdebug(None)
import gc
import webrepl

def do_connect():
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.config(dhcp_hostname="FrontOutsideLightESP_STA")
        sta_if.connect('NETGEAR41', 'xxxxxxxx')
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(True)
    ap_if.config(essid='FrontOutsideLightESP')

do_connect()
webrepl.start()
gc.collect()
