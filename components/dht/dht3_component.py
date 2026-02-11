import threading
import time
from common.locks import print_lock
from common.mqqt_sender import batch_queue
from simulators.dht3_simulator import run_dht3_simulator

def dht3_callback(code, device_info, settings, temperature, humidity):
    payload = {
        "measurement": "Kitchen DHT",
        "device_name": device_info['device_name'],
        "pi_id": device_info['pi_id'],
        "code": code,
        "temperature": temperature,
        "humidity": humidity,
        "simulated": settings['simulated'] 
    }
    batch_queue.put(payload) 
    print(f"[{code}] Sent to buffer: Temp: {temperature}°C, Hum: {humidity}%")

def real_dht3_loop(settings, stop_event, device_info):
    import RPi.GPIO as GPIO
    from .LA_DHT import DHT
    
    DHTPin = settings["pin"] 
    dht = DHT(DHTPin)
    code = settings['code']
    
    while not stop_event.is_set():
        chk = dht.readDHT11()
        if chk == dht.DHTLIB_OK:
            dht3_callback(code, device_info, settings, dht.temperature, dht.humidity)
        
        time.sleep(settings.get('delay', 2))

def run_dht3(settings, threads, stop_event, device_info):
    if settings['simulated']:
        code = settings['code']
        print(f'Starting {code} simulator')
        
        dht_thread = threading.Thread(
            target=run_dht3_simulator, 
            args=(settings['delay'], lambda c, t, h: dht3_callback(c, device_info, settings, t, h), stop_event, code)
        )
        dht_thread.start()
        threads.append(dht_thread)
        print("Kitchen DHT simulator started")
    else:
        print(f"Starting {device_info['device_name']} real sensor")
        dht_thread = threading.Thread(target=real_dht3_loop, args=(settings, stop_event, device_info))
        dht_thread.start()
        threads.append(dht_thread)
        print("Kitchen DHT real sensor started")