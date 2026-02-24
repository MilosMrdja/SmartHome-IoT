import threading
from common.mqqt_sender import batch_queue
from simulators.dpir3_simulator import run_dpir3_simulator

def dpir3_callback(code, device_info, settings):
    payload = {
        "measurement": "Living_Room_Motion_Sensor",
        "device_name": device_info['device_name'],
        "pi_id": device_info['pi_id'],
        "code": code,
        "value": 1,
        "simulated": settings['simulated'],
        "people_count": None
    }
    batch_queue.put(payload) 
    print(f"[{code}] Sent to buffer: motion detected in living room")

def run_dpir3(settings, threads, stop_event, device_info):
        if settings['simulated']:
            code = settings['code']
            print(f'Starting {code} simulator')
            dpir3_thread = threading.Thread(target = run_dpir3_simulator, args=(settings['delay'], lambda c: dpir3_callback(c, device_info, settings), stop_event, code))
            dpir3_thread.start()
            threads.append(dpir3_thread)
            print("DPIR3 simulator started")
        else:
            import RPi.GPIO as GPIO
            port_btn = settings['pin']
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(port_btn, GPIO.IN)
            GPIO.add_event_detect(port_btn, GPIO.RISING, callback=lambda c: dpir3_callback(settings['code'], device_info, settings))
            print("DPIR3 real sensor real sensor started")
