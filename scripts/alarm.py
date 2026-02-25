import threading
import time
import paho.mqtt.client as mqtt
import json
from common.mqqt_sender import batch_queue
from simulators.db_simulator import set_buzzer_state

send_turn_on = False
send_turn_off = False

def turn_alarm_on(device_info, settings, from_server = False):
    global send_turn_on, send_turn_off
    if from_server:
        set_buzzer_state(True)
        print(f"!!! ALARM WAS ACTIVATED!!!")
    else:
        if not send_turn_on:
            payload = {
                "measurement": "alarm_events",
                "device_name": device_info['device_name'],
                "pi_id": device_info['pi_id'],
                "code": settings["code"],
                "simulated" : settings['simulated'],
                "value": 1
            }
            print(payload)
            send_turn_on = True
            send_turn_off = False
            batch_queue.put(payload)

def turn_alarm_off(device_info, from_server = False):
    global send_turn_on, send_turn_off
    if from_server:
        set_buzzer_state(False)
        print("ALARM WAS DEACTIVATED")
    else:    
        if not send_turn_off:
            payload = {
                "measurement": "alarm_events",
                "device_name": device_info['device_name'],
                "pi_id": device_info['pi_id'],
                "code": "PIN_OR_WEB_DEACTIVATION",
                "value": 0 
            }
            print(payload)
            send_turn_off = True
            send_turn_on = False
            batch_queue.put(payload)

def on_connect(client, userdata, flags, rc):
    client.subscribe("commands/alarm")
    print("Alarm listener connected and subscribed to commands/alarm")

def on_message(client, userdata, msg, device_info):
    try:
        data = json.loads(msg.payload.decode())
        if data['command'] == 'ON':
            turn_alarm_on(device_info, {"code": data.get('code', 'REMOTE_COMMAND')}, from_server=True)
        elif data['command'] == 'OFF':
            turn_alarm_off(device_info, from_server=True)
    except Exception as e:
        print(f"Error processing alarm command: {e}")

def run_alarm_listener(device_info, mqtt_settings):
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = lambda c, u, m: on_message(c, u, m, device_info)
    
    client.connect(mqtt_settings['broker_hostname'], mqtt_settings['port'], 60)
    client.loop_forever()