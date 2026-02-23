import threading
import time
from simulators.db_simulator import get_buzzer_state, run_db_simulator
from common.locks import print_lock

from common.mqqt_sender import batch_queue

_settings = None
_device_info = None

def db_callback(state, code, settings, device_info):
    payload = {
        "measurement": "buzzer_state",
        "device_name": device_info['device_name'],
        "pi_id": device_info['pi_id'],
        "code": code,
        "value": 1 if state else 0,
        "simulated": settings['simulated']
    }
    batch_queue.put(payload)
    print(f"[{code}] Sent to buffer: {'ON' if state else 'OFF'}")


def turn_on_db_logic():
    pass

def run_db(settings, threads, stop_event, device_info):
    global _settings, _device_info
    _settings = settings
    _device_info = device_info
    if settings['simulated']:
        pitch = settings.get('pitch', 440)
        duration = settings.get('duration', 0.1)
        code = settings['code']
        print(f"Starting {code} simulator")
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
        GPIO.setmode(GPIO.BCM)
        buzzer_pin = settings["pin"]
        GPIO.setup(buzzer_pin, GPIO.OUT)

        def buzz(pitch, duration):
            period = 1.0 / pitch
            delay = period / 2
            cycles = int(duration * pitch)
            for i in range(cycles):
                GPIO.output(buzzer_pin, True)
                time.sleep(delay)
                GPIO.output(buzzer_pin, False)
                time.sleep(delay)

        last_state = False
        try:
            while not stop_event.is_set():
                current_state = get_buzzer_state()

                if current_state and not last_state:
                    db_callback(True, code, settings, device_info)
                    last_state = True
                
                elif not current_state and last_state:
                    db_callback(False, code, settings, device_info)
                    last_state = False

                if current_state:
                    buzz(settings["pitch"], settings["duration"])
                
                time.sleep(0.1)
        except KeyboardInterrupt:
            GPIO.cleanup()
