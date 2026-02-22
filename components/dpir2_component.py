import threading
import time
from common.locks import print_lock
from common.mqqt_sender import batch_queue
from scripts.people_counter import process_motion
from simulators.dpir2_simulator import run_dpir2_simulator

def dpir2_callback(code, device_info, settings):
    motion = process_motion(sensor_id=2)
    payload = {
        "measurement": "door pir 2",
        "device_name": device_info['device_name'],
        "pi_id": device_info['pi_id'],
        "code": code,
        "value": 1,
        "simulated": settings['simulated'],
        "people_count": motion
    }
    batch_queue.put(payload) 
    print(payload)
    print(f"[{code}] Sent to buffer: motion detected")

def run_dpir2(settings, threads, stop_event, device_info):
        if settings['simulated']:
            code = settings['code']
            print(f'Starting {code} simulator')
            dpir1_thread = threading.Thread(target = run_dpir2_simulator, args=(settings['delay'], lambda c: dpir2_callback(c, device_info, settings), stop_event, code))
            dpir1_thread.start()
            threads.append(dpir1_thread)
            print("DPIR2 simulator started")
        else:
            import RPi.GPIO as GPIO
            port_btn = settings['pin']
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(port_btn, GPIO.IN)
            GPIO.add_event_detect(port_btn, GPIO.RISING, callback=lambda c: dpir2_callback(settings['code'], device_info, settings))
