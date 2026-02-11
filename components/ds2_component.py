import threading
import time
from common.locks import print_lock
from common.mqqt_sender import batch_queue
from simulators.ds2_simulator import run_ds2_simulator

def ds2_callback(code, device_info, settings):
    payload = {
        "measurement": "button door 2",
        "device_name": device_info['device_name'],
        "pi_id": device_info['pi_id'],
        "code": code,
        "value": 1,
        "simulated": settings['simulated'] # Tag da li je simulirano
    }
    batch_queue.put(payload) # Dodavanje u red (Thread-safe)
    print(f"[{code}] Sent to buffer: button 2 pressed")

def run_ds2(settings, threads, stop_event, device_info):
        if settings['simulated']:
            delay = settings['delay']
            code = settings['code']
            print(f"Starting {code} simulator")
            ds1_thread = threading.Thread(target = run_ds2_simulator, args=(delay, lambda c, d, s: ds2_callback(c, d, s), stop_event, code, device_info, settings))
            ds1_thread.start()
            threads.append(ds1_thread)
            print("DS2 sumilator started")
        else:
            import RPi.GPIO as GPIO
            port_btn = settings['pin']
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(port_btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(port_btn, GPIO.RISING, callback=lambda c: ds2_callback(settings['code'], device_info, settings), bouncetime = 100)