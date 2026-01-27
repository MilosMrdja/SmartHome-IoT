import paho.mqtt.publish as publish
import json
import threading
import time
from queue import Queue

# Deljeni red za sve senzore na PI1
batch_queue = Queue()

def mqtt_batch_daemon(mqtt_settings, stop_event):
    batch = []
    while not stop_event.is_set():
        while not batch_queue.empty():
            batch.append(batch_queue.get())
        
        if batch:
            try:
                publish.single(
                    mqtt_settings['topic'],
                    payload=json.dumps(batch),
                    hostname=mqtt_settings['broker_hostname'],
                    port=mqtt_settings['port']
                )
                print(f"[MQTT] Sent batch of {len(batch)} readings.")
            except Exception as e:
                print(f"[MQTT] Error: {e}")
            
            batch = []
        
        time.sleep(5) 