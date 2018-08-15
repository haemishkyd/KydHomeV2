import machine
import time
import onewire
import ds18x20
import network
#import webrepl_setup
from umqtt.simple import MQTTClient

CONFIG = {
    "broker": "192.168.1.100",
    "client_id": "Front Outside Temp",
    "p1_topic": "homeassistant/sensor/frontoutsidetemperature/temp",
    "broadcast_topic": "homeassistant/sensor/frontoutsidetemperature/ip",
}

def do_mqtt_connect(l_client):
    try:        
        l_client.connect()
        print("Connected to {}".format(CONFIG['broker']))        
    except OSError as e:
        machine.reset()
    

def get_current_milliseconds():    
    return time.ticks_ms()


wlan = network.WLAN(network.STA_IF)
client = MQTTClient(CONFIG['client_id'], CONFIG['broker'])
do_mqtt_connect(client)
main_scheduler_counter = 0
ip = wlan.ifconfig()[0]

# the device is on GPIO12
dat = machine.Pin(12)

# create the onewire object
ds = ds18x20.DS18X20(onewire.OneWire(dat))

# scan for devices on the bus
roms = ds.scan()
print('found devices:', roms)
current_temp = 0

temp_send_timer = get_current_milliseconds()
ip_send_timer = get_current_milliseconds()
get_temp_timer = get_current_milliseconds()

while True:   
    try:
        if ((get_current_milliseconds() - temp_send_timer) > 10000):
            print("Outside Temperature: Send Temp")
            client.publish(CONFIG['p1_topic'],
                           "{\"temp\":" + str(current_temp) + "}")
            temp_send_timer = get_current_milliseconds()

        if ((get_current_milliseconds() - ip_send_timer) > 10000):
            print("Outside Temp Sensor: Send IP Info")
            payload = CONFIG['client_id']
            client.publish(CONFIG['broadcast_topic'],
                           "{\"ip\":\"" + ip + "\"}")
            ip_send_timer = get_current_milliseconds()    

        if ((get_current_milliseconds() - get_temp_timer) > 1000):
            print("Outside Temp Sensor: Retrieve Temp")
            try:
                ds.convert_temp()
                for rom in roms:
                    current_temp = ds.read_temp(rom)
                    print(current_temp)
            except:
                print("Outside Temp Sensor: Conversion Failed")
            get_temp_timer = get_current_milliseconds()

    except OSError as e:
        do_mqtt_connect(client)
        time.sleep(5)
    

machine.reset()
