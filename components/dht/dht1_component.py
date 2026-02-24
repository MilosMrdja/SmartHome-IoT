import threading
import time
from common.locks import print_lock
from common.mqqt_sender import batch_queue
from simulators.dht1_simulator import run_dht1_simulator
from simulators.lcd_simulator import set_lcd_state


def dht1_callback(code, device_info, settings, temperature, humidity):
    
    line1 = f"Temp: {temperature} C"
    line2 = f"Hum:  {humidity} %"
    
    try:
        set_lcd_state(line1, line2)
    except Exception as e:
        print(f"LCD not initialized yet: {e}")

    payload = {
        "measurement": "Bedroom_DHT",
        "device_name": device_info['device_name'],
        "pi_id": device_info['pi_id'],
        "code": code,
        "temperature": temperature,
        "humidity": humidity,
        "simulated": settings['simulated'] 
    }
    batch_queue.put(payload) 
    print(f"[{code}] Sent to buffer & LCD: T: {temperature}C, H: {humidity}%")

def real_dht1_loop(settings, stop_event, device_info):
    import RPi.GPIO as GPIO
    from .LA_DHT import DHT
    
    DHTPin = settings["pin"] 
    dht = DHT(DHTPin)
    code = settings['code']
    
    while not stop_event.is_set():
        chk = dht.readDHT11()
        if chk == dht.DHTLIB_OK:
            dht1_callback(code, device_info, settings, dht.temperature, dht.humidity)
        
        time.sleep(settings.get('delay', 2))

def run_dht1(settings, threads, stop_event, device_info):
    if settings['simulated']:
        code = settings['code']
        print(f'Starting {code} simulator')
        
        dht1_thread = threading.Thread(
            target=run_dht1_simulator, 
            args=(settings['delay'], lambda c, t, h: dht1_callback(c, device_info, settings, t, h), stop_event, code)
        )
        dht1_thread.start()
        threads.append(dht1_thread)
        print("Bedroom DHT simulator started")
    else:
        print(f"Starting {device_info['device_name']} real sensor")
        dht1_thread = threading.Thread(target=real_dht1_loop, args=(settings, stop_event, device_info))
        dht1_thread.start()
        threads.append(dht1_thread)
        print("Bedroom DHT real sensor started")