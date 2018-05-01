import machine
import time
import network
#import webrepl_setup
from umqtt.simple import MQTTClient

CONFIG = {
    "broker": "192.168.1.100",
    "client_id": "POOL PUMP",
    "p1_topic": "homeassistant/sensor/poolpump/state",
    "s1_topic": "homeassistant/switch/poolpump/state",
    "broadcast_topic": "homeassistant/sensor/poolpump/ip",
}

def subscription_callback(topic,msg):
    global pump_cmd_pin
    if topic == CONFIG['s1_topic'].encode('utf8'):
        if msg == b"ON":
            print ("Pool Pump On")            
            pump_cmd_pin.value(0)
        if msg == b"OFF":
            print("Pool Pump Off")            
            pump_cmd_pin.value(1)


def check_subs(l_client):
    # print("Pool: Check Subs")
    l_client.check_msg()


def publish_state(l_client, l_pool_pump_state):
    print("Pool Pump: Send P1")
    if (l_pool_pump_state == 0):
        l_client.publish(CONFIG['p1_topic'], "{\"state\":\"ON\"}")
    else:
        l_client.publish(CONFIG['p1_topic'], "{\"state\":\"OFF\"}")


def broadcast_details(l_client, ip):
    print("Pool Pump: Send Broadcast")
    l_client.publish(CONFIG['broadcast_topic'],
                     "{\"ip\":\"" + ip + "\"}")


def do_mqtt_connect(l_client):
    try:        
        l_client.connect()
        print("Connected to {}".format(CONFIG['broker']))
        l_client.subscribe(CONFIG['s1_topic'])
    except OSError as e:
        machine.reset()
    

def get_current_milliseconds():
    return time.ticks_ms()


wlan = network.WLAN(network.STA_IF)

client = MQTTClient(CONFIG['client_id'], CONFIG['broker'])
client.set_callback(subscription_callback)
do_mqtt_connect(client)
pool_pump_state = 0
# set up the pool pump pin and initialise the RELAY to off
pump_cmd_pin = machine.Pin(5, machine.Pin.OUT)
pump_cmd_pin.value(1)
time.sleep(5)
ip = wlan.ifconfig()[0]

check_subs_timer = get_current_milliseconds()
send_state_timer = get_current_milliseconds()
ip_send_timer = get_current_milliseconds()

while True:   
    try:        
        if ((get_current_milliseconds() - check_subs_timer) > 100):
            check_subs(client)
            check_subs_timer = get_current_milliseconds()

        if ((get_current_milliseconds() - send_state_timer) > 1000):
            pool_pump_state = pump_cmd_pin.value()
            publish_state(client, pool_pump_state)
            send_state_timer = get_current_milliseconds()
        
        if ((get_current_milliseconds() - ip_send_timer) > 10000):
            broadcast_details(client, ip)
            ip_send_timer = get_current_milliseconds()

    except OSError as e:
        do_mqtt_connect(client)
        time.sleep(5)
    
machine.reset()
