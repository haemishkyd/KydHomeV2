#!/usr/bin/python
import paho.mqtt.client as mqtt
import time

MonitorList = {"homeassistant/sensor/frontoutsidelight/ip": 0,
               "homeassistant/sensor/gate/ip":0,
               "homeassistant/sensor/frontoutsidetemperature/ip":0,
               "homeassistant/sensor/poolpump/ip":0,
               "homeassistant/sensor/paradox/ip": 0}


def current_milli_time(): 
    return int(round(time.time() * 1000))

def logdiagdata(logstring):
    time_log_string = '{}-{}-{} {}:{}'.format(time.strftime("%d"), time.strftime(
        "%m"), time.strftime("%Y"), time.strftime("%H:%M:%S"), logstring)
    print(time_log_string)
    target_log = open("remote_control_service.log", 'a')
    target_log.write(time_log_string + "\n\r")
    target_log.close()

# The callback for when the client receives a CONNACK response from the server.


def on_connect(client, userdata, flags, rc):
    global Connected
    logdiagdata("Connected with result code " + str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    for key, value in MonitorList.items():
        client.subscribe(key)
    Connected = True

def on_disconnect(client, userdata, rc):
    global Connected
    Connected = False

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):    
    MonitorList[msg.topic] = current_milli_time()
    # logdiagdata(msg.topic + ":" + str(MonitorList[msg.topic]))
    
def on_publish(mosq, obj, mid):
    logdiagdata("mid: " + str(mid))

def on_subscribe(mosq, obj, mid, granted_qos):
    logdiagdata("Subscribed: " + str(mid) + " " + str(granted_qos))

def main():
    global Connected
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_publish = on_publish
    client.on_subscribe = on_subscribe
    client.on_disconnect = on_disconnect

    while True:
        if (Connected == False):
            try:
                client.connect("192.168.1.100", 1883, 60)
                client.loop_start()
                logdiagdata("Connecting!")
                time.sleep(1)
            except:
                logdiagdata("Could not connect - trying again!")
                time.sleep(5)
        time.sleep(10)
        for key, value in MonitorList.items():
            print(key+":"+str((current_milli_time()-value)/1000))
        print("*********************************************")


Connected = False
target_log = open("mqtt_online.log", 'w')
target_log.write("File Log Start.....")
target_log.close()
logdiagdata("Waiting for startup to be complete...")
time.sleep(10)
logdiagdata("Startup complete!")

for key, value in MonitorList.items():
    MonitorList[key] = current_milli_time()

main()

