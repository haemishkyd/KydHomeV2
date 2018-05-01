import machine
import time
import network
#import webrepl_setup
from umqtt.simple import MQTTClient

CONFIG = {
    "broker": "192.168.1.100",
    "client_id": "FRONT OUTSIDE LIGHT",
    "p1_topic": "homeassistant/sensor/frontoutsidelight/state",
    "s1_topic": "homeassistant/switch/frontoutsidelight/state",
    "broadcast_topic": "homeassistant/sensor/frontoutsidelight/ip",
}
                    
def subscription_callback(topic,msg):
    global light_cmd_pin
    if topic == CONFIG['s1_topic'].encode('utf8'):
        if msg == b"ON":
            print ("Outside Light On")
            light_cmd_pin.value(1)
        if msg == b"OFF":
            print("Outside Light Off")
            light_cmd_pin.value(0)


def do_mqtt_connect(l_client):
    try:        
        l_client.connect()
        print("Connected to {}".format(CONFIG['broker']))
        l_client.subscribe(CONFIG['s1_topic'])
    except OSError as e:
        print ("Could not connect!!")


def check_subs(l_client):
    # print("Front Outside Light: Check Subs")
    l_client.check_msg()


def publish_state(l_client, l_outside_light_state):
    print("Front Outside Light: Send P1")
    if (l_outside_light_state == 1):
        l_client.publish(CONFIG['p1_topic'], "{\"state\":\"ON\"}")
    else:
        l_client.publish(CONFIG['p1_topic'], "{\"state\":\"OFF\"}")
    

def broadcast_details(l_client, ip):
    print("Front Outside Light: Send Broadcast")
    l_client.publish(CONFIG['broadcast_topic'],
                   "{\"ip\":\"" + ip + "\"}")


def get_current_milliseconds():
    return time.ticks_ms()


#setup the info for id broadcast
wlan = network.WLAN(network.STA_IF)

client = MQTTClient(CONFIG['client_id'], CONFIG['broker'])
client.set_callback(subscription_callback)
do_mqtt_connect(client)
outside_light_state = 0
# set up the outside light pin and initialise the RELAY to off
light_cmd_pin = machine.Pin(5, machine.Pin.OUT)
# make the light on by default
light_cmd_pin.value(1)
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
            outside_light_state = light_cmd_pin.value()
            publish_state(client,outside_light_state)
            send_state_timer = get_current_milliseconds()

        if ((get_current_milliseconds() - ip_send_timer) > 10000):
            broadcast_details(client, ip)
            ip_send_timer = get_current_milliseconds()
        
    except OSError as e:
        do_mqtt_connect(client)
        state_machine_variable = 0
        publish_counter = 0
        time.sleep(5)
    

machine.reset()
