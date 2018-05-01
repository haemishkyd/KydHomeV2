import machine
import time
import network
#import webrepl_setup
from umqtt.simple import MQTTClient

CONFIG = {
    "broker": "192.168.1.100",
    "client_id": "GATE TERMINAL",
    "p1_topic": "homeassistant/sensor/gatelight/state",
    "p2_topic": "homeassistant/sensor/gateactual/state",
    "s1_topic": "homeassistant/switch/gatelight/state",
    "s2_topic": "homeassistant/switch/gateactual/state",
    "broadcast_topic": "homeassistant/sensor/gate/ip",
}

def subscription_callback(topic,msg):
    global gate_open_cmd_pin
    global gate_light_pin    
    if topic == CONFIG['s1_topic'].encode('utf8'):
        if msg == b"ON":
            print ("Gate Light On")
            gate_light_pin.value(0)
        if msg == b"OFF":
            print ("Gate Light Off")
            gate_light_pin.value(1)
    if topic == CONFIG['s2_topic'].encode('utf8'):
        if msg == b"ON":
            print ("Gate Inactive")
            gate_open_cmd_pin.value(0)
        if msg == b"OFF":
            print ("Gate Active")
            gate_open_cmd_pin.value(1)

def do_mqtt_connect(l_client):
    try:        
        l_client.connect()
        print("Connected to {}".format(CONFIG['broker']))
        l_client.subscribe(CONFIG['s1_topic'])
        l_client.subscribe(CONFIG['s2_topic'])
    except OSError as e:        
        machine.reset()
    

def check_subs(l_client):
    # print("Front Outside Light: Check Subs")
    l_client.check_msg()


def publish_state(l_client, l_gate_open_state,l_gate_light_state):
    print("Gate Terminal: Send P1")
    if (l_gate_light_state == 1):
        client.publish(CONFIG['p1_topic'], "{\"state\":\"OFF\"}")
    else:
        client.publish(CONFIG['p1_topic'], "{\"state\":\"ON\"}")
    print("Gate Terminal: Send P2")
    if (gate_open_in_pin.value() == 1):
        client.publish(CONFIG['p2_topic'], "{\"state\":\"OFF\"}")
    else:
        client.publish(CONFIG['p2_topic'], "{\"state\":\"ON\"}")


def broadcast_details(l_client, ip):
    print("Gate: Send Broadcast")
    l_client.publish(CONFIG['broadcast_topic'],
                     "{\"ip\":\"" + ip + "\"}")


def get_current_milliseconds():
    return time.ticks_ms()


#setup the info for id broadcast
wlan = network.WLAN(network.STA_IF)

client = MQTTClient(CONFIG['client_id'], CONFIG['broker'])
client.set_callback(subscription_callback)
do_mqtt_connect(client)
gate_open_state = 0
# set up the gate command pin and initialise the RELAY to off
gate_open_cmd_pin = machine.Pin(4, machine.Pin.OUT)
gate_open_cmd_pin.value(1)
# set up the gate light pin and initialise the RELAY to off
gate_light_pin = machine.Pin(5, machine.Pin.OUT)
gate_light_pin.value(1)
# the gate reed switch is shorted when closed. The pullups are required to make it high
# when the gate is open
gate_open_in_pin = machine.Pin(13, machine.Pin.IN, machine.Pin.PULL_UP)
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
            gate_open_state = gate_open_in_pin.value()
            gate_light_state = gate_light_pin.value()
            publish_state(client, gate_open_state, gate_light_state)
            send_state_timer = get_current_milliseconds()

        if ((get_current_milliseconds() - ip_send_timer) > 10000):
            broadcast_details(client, ip)
            ip_send_timer = get_current_milliseconds()

    except OSError as e:
        do_mqtt_connect(client)
        time.sleep(5)
    

machine.reset()
