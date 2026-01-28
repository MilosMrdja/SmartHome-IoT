import threading
import time
from simulators.dl_simulator import run_dl_simulator
from common.locks import print_lock
#import RPi.GPIO as GPIO
from common.mqqt_sender import batch_queue

def dl_callback(state, code, settings, device_info):
    payload = {
        "measurement": "light_state",
        "device_name": device_info['device_name'],
        "pi_id": device_info['pi_id'],
        "code": code,
        "value": 1 if state else 0,
        "simulated": settings['simulated'] # Tag da li je simulirano
    }
    batch_queue.put(payload) # Dodavanje u red (Thread-safe)
    
    # Tvoj stari print log
    print(f"[{code}] Sent to buffer: {'ON' if state else 'OFF'}")


def run_dl(settings, threads, stop_event, device_info):
        if settings['simulated']:
            delay = settings['delay']
            code = settings['code']
            print("Starting {code} simulator")

            # Lambda se koristi da bi callback dobio i settings i device_info
            dl_thread = threading.Thread(
                target=run_dl_simulator, 
                args=(delay, lambda s, c: dl_callback(s, c, settings, device_info), stop_event, code)
            )
            dl_thread.start()
            threads.append(dl_thread)
            print("Dl simulator started")
        else:
            '''pin = settings['pin']
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

            def sensor_callback(channel):
                # Logika za pravi senzor (npr. detekcija nivoa svetlosti ili prekidača)
                reading = GPIO.input(pin)
                payload = {
                    "measurement": "Device_Logic",
                    "device_name": device_info['device_name'],
                    "pi_id": device_info['pi_id'],
                    "code": settings['code'],
                    "value": reading,
                    "simulated": False
                }
                batch_queue.put(payload)

            # Postavljanje interrupt-a da ne bismo trošili CPU u while petlji
            GPIO.add_event_detect(pin, GPIO.BOTH, callback=sensor_callback, bouncetime=200)
            print(f"Real sensor {settings['code']} initialized on pin {pin}")'''