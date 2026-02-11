import threading
import time
from simulators.db_simulator import run_db_simulator
from common.locks import print_lock

from common.mqqt_sender import batch_queue

def db_callback(state, code, settings, device_info):
    payload = {
        "measurement": "buzzer_state",
        "device_name": device_info['device_name'],
        "pi_id": device_info['pi_id'],
        "code": code,
        "value": 1 if state else 0,
        "simulated": settings['simulated'] # Tag da li je simulirano
    }
    batch_queue.put(payload) # Dodavanje u red (Thread-safe)
    print(f"[{code}] Sent to buffer: {'ON' if state else 'OFF'}")

def run_db(settings, threads, stop_event, device_info):
    if settings['simulated']:
        print("Starting DB simulator")

        pitch = settings.get('pitch', 440)
        duration = settings.get('duration', 0.1)
        code = settings['code']
        print("Starting {code} simulator")
        delay = settings['delay']


        db_thread = threading.Thread(
            target=run_db_simulator,
            args=(delay,  lambda s, c: db_callback(s, c, settings, device_info), stop_event, code, pitch, duration),
            daemon=True
        )

        db_thread.start()
        threads.append(db_thread)

        print("DB simulator started")
    else:
        code = settings['code']
        import RPi.GPIO as GPIO
        import time
        GPIO.setmode(GPIO.BCM)
        buzzer_pin = settings["pin"]
        GPIO.setup(buzzer_pin, GPIO.OUT)
        def buzz(pitch, duration):
            period = 1.0 / pitch
            delay = period / 2
            cycles = int(duration * pitch)
            for i in range(cycles):
                GPIO.output(buzzer_pin, True)
                db_callback(True, code, settings, device_info)
                time.sleep(delay)
                GPIO.output(buzzer_pin, False)
                db_callback(False, code, settings, device_info)
                time.sleep(delay)
        try:
            while True:
                pitch = settings["pitch"]
                duration = settings["duration"]
                buzz(pitch, duration)
                time.sleep(1)
        except KeyboardInterrupt:
            GPIO.cleanup()
