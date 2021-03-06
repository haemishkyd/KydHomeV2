import time
from subprocess import check_output
import re
import paho.mqtt.client as mqtt

class PowerData:
    power_state = 2
    power_percent = 0
    input_voltage = 0
    output_voltage = 0
    battery_voltage = 0
    mqtt_connected = False

    old_power_state = 2
    old_power_percent = 0
    old_input_voltage = 0
    old_output_voltage = 0
    old_battery_voltage = 0
    old_mqtt_connected = False

    def __init__(self):
        logdiagdata("Power Class Created\n\r")

    def flush(self):
        logdiagdata("Flush all data.")
        self.old_power_state = 2
        self.old_power_percent = 0
        self.old_input_voltage = 0
        self.old_output_voltage = 0
        self.old_battery_voltage = 0
        self.old_mqtt_connected = False

def logdiagdata(logstring):
    global target_log       
    time_log_string = '{}-{}-{} {}:{}'.format(time.strftime("%d"),time.strftime("%m"),time.strftime("%Y"),time.strftime("%H:%M:%S"),logstring)
    print(time_log_string)
    target_log.write(time_log_string+"\n\r")

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    logdiagdata("Connected with result code "+str(rc))
    userdata.mqtt_connected = True
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # client.subscribe("$SYS/#")

def on_disconnect(client, userdata, rc):
    userdata.mqtt_connected = False
    logdiagdata("Disconnected with result code "+str(rc))

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    logdiagdata(msg.topic+" "+str(msg.payload))

def on_publish(mosq, obj, mid):
    logdiagdata("Published: " + str(mid))

def on_subscribe(mosq, obj, mid, granted_qos):
    logdiagdata("Subscribed: " + str(mid) + " " + str(granted_qos))

def runPowerQuery(client,pd):
    out = check_output(['upsc', 'mecer'], universal_newlines=True) 
    #print out   
    lines = out.split('\n')

    for line in lines:
        matchObj = re.match(r'(ups.status: )(.*)',line)
        if matchObj:
            if matchObj.group(2) == "OL":
                pd.power_state = 1
                if pd.old_power_state != pd.power_state:
                    l_mqtt_publish(client,"homeassistant/sensor/powersystem/powerstatus","PG")
            else:
                pd.power_state = 0
                if pd.old_power_state != pd.power_state:
                    l_mqtt_publish(client,"homeassistant/sensor/powersystem/powerstatus","PF")
                pd.old_power_state = pd.power_state

        matchObj = None 
        matchObj = re.match(r'(battery.charge: )(.*)',line)
        if matchObj:
            pd.power_percent = int(float(matchObj.group(2)))             
            if pd.old_power_percent != pd.power_percent:
                logdiagdata("Battery Charge: "+str(pd.power_percent))
                l_mqtt_publish(client,"homeassistant/sensor/powersystem/powerpercent",pd.power_percent)
                pd.old_power_percent = pd.power_percent

        matchObj = None 
        matchObj = re.match(r'(input.voltage: )(.*)',line)
        if matchObj:            
            pd.input_voltage = int(float(matchObj.group(2)))            
            if pd.old_input_voltage != pd.input_voltage:
                logdiagdata("Input Voltage: "+str(pd.input_voltage))
                l_mqtt_publish(client,"homeassistant/sensor/powersystem/inputvoltage",pd.input_voltage)
                pd.old_input_voltage = pd.input_voltage

        matchObj = None 
        matchObj = re.match(r'(output.voltage: )(.*)',line)
        if matchObj:            
            pd.output_voltage = int(float(matchObj.group(2)))            
            if pd.old_output_voltage != pd.output_voltage:
                logdiagdata("Output Voltage: "+str(pd.output_voltage)) 
                l_mqtt_publish(client,"homeassistant/sensor/powersystem/outputvoltage",pd.output_voltage)         
                pd.old_output_voltage = pd.output_voltage

        matchObj = None 
        matchObj = re.match(r'(battery.voltage: )(.*)',line)
        if matchObj:            
            pd.battery_voltage = float(matchObj.group(2))     
            logdiagdata("Got UPS Data...")       
            if pd.old_battery_voltage != pd.battery_voltage:
                logdiagdata("Battery Voltage: "+str(pd.battery_voltage))
                l_mqtt_publish(client,"homeassistant/sensor/powersystem/batteryvoltage",pd.battery_voltage)            
                pd.old_battery_voltage = pd.battery_voltage

def l_mqtt_publish(client,topic,data):
    try:
        client.publish(topic,data)            
    except:
        logdiagdata("Could not publish to topic "+topic)
        client.disconnect()

target_log = open("powermon.log",'w')
target_log.write("File Log Start.....")
logdiagdata("Waiting for startup to be complete...")
time.sleep(20)
logdiagdata("Startup complete!")
p = PowerData()
client = mqtt.Client(userdata=p)
client.on_connect       = on_connect
client.on_message       = on_message
client.on_publish       = on_publish
client.on_subscribe     = on_subscribe
client.on_disconnect    = on_disconnect
flush_counter = 0

while True:            
    if p.mqtt_connected == False:
        logdiagdata("Connecting")
        try:
            client.connect("192.168.1.100", 1883, 60)
            client.loop_start()
        except:
            logdiagdata("Broker not responding. Retrying in 10 seconds.")
            p.flush()
            time.sleep(10)
    # client.loop()
    runPowerQuery(client,p)
    flush_counter = flush_counter + 1
    time.sleep(1)
    if (flush_counter > 30):
        logdiagdata("Data Flush")
        p.flush()
        flush_counter = 0