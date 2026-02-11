import threading
import time
from common.mqqt_sender import batch_queue
from simulators.webc_simulator import run_webc_simulator


def webc_callback(distance, code, device_info, settings):
    payload = {
        "measurement": "door ultrasonic 1",
        "device_name": device_info['device_name'],
        "pi_id": device_info['pi_id'],
        "code": code,
        "value": distance,
        "simulated": settings['simulated'] 
    }
    batch_queue.put(payload) 
    print(f"[{code}] Sent to buffer: web camera")

def run_webc(settings, threads, stop_event, device_info):
    if settings['simulated']:
        delay = settings['delay']
        code = settings['code']
        print(f'Starting {code} simulator')
        dus1_thread = threading.Thread(target=run_webc_simulator, args=(delay, lambda d, c: webc_callback(d, c, device_info, settings), stop_event, code))          
        dus1_thread.start()
        threads.append(dus1_thread)
    else:
        pass
