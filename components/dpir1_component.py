import threading
import time
from simulators.dpir1_simulator import run_dpir1_simulator
from common.locks import print_lock
from common.mqqt_sender import batch_queue

def dpir1_callback(code, device_info, settings):
    payload = {
        "measurement": "door pir 1",
        "device_name": device_info['device_name'],
        "pi_id": device_info['pi_id'],
        "code": code,
        "value": 1,
        "simulated": settings['simulated'],
        "people_count": True
    }
    batch_queue.put(payload) 
    print(f"[{code}] Sent to buffer: motion detected")

def run_dpir1(settings, threads, stop_event, device_info):
        if settings['simulated']:
            code = settings['code']
            print(f'Starting {code} simulator')
            dpir1_thread = threading.Thread(target = run_dpir1_simulator, args=(settings['delay'], lambda c: dpir1_callback(c, device_info, settings), stop_event, code))
            dpir1_thread.start()
            threads.append(dpir1_thread)
            print("DPIR1 simulator started")
        else:
            import RPi.GPIO as GPIO
            port_btn = settings['pin']
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(port_btn, GPIO.IN)
            GPIO.add_event_detect(port_btn, GPIO.RISING, callback=lambda c: dpir1_callback(settings['code'], device_info, settings))
