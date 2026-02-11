import threading
import time
from common.locks import print_lock
from common.mqqt_sender import batch_queue
from simulators.btn_simulator import run_btn_simulator

def btn_callback(code, device_info, settings):
    payload = {
        "measurement": "kitchen button",
        "device_name": device_info['device_name'],
        "pi_id": device_info['pi_id'],
        "code": code,
        "value": 1,
        "simulated": settings['simulated'] # Tag da li je simulirano
    }
    batch_queue.put(payload) # Dodavanje u red (Thread-safe)
    print(f"[{code}] Sent to buffer: kitchen button pressed")

def run_btn(settings, threads, stop_event, device_info):
        if settings['simulated']:
            delay = settings['delay']
            code = settings['code']
            print(f"Starting {code} simulator")
            ds1_thread = threading.Thread(target = run_btn_simulator, args=(delay, lambda c, d, s: btn_callback(c, d, s), stop_event, code, device_info, settings))
            ds1_thread.start()
            threads.append(ds1_thread)
            print("BTN sumilator started")
        else:
            import RPi.GPIO as GPIO
            port_btn = settings['pin']
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(port_btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(port_btn, GPIO.RISING, callback=lambda c: btn_callback(settings['code'], device_info, settings), bouncetime = 100)