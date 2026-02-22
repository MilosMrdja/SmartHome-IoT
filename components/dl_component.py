import threading
import time
from simulators.dl_simulator import run_dl_simulator, set_led_state
from common.locks import print_lock
#import RPi.GPIO as GPIO
from common.mqqt_sender import batch_queue


_settings = None
_device_info = None

def dl_callback(state, code, settings, device_info):
    payload = {
        "measurement": "light_state",
        "device_name": device_info['device_name'],
        "pi_id": device_info['pi_id'],
        "code": code,
        "value": 1 if state else 0,
        "simulated": settings['simulated']
    }
    batch_queue.put(payload)
    print(f"[{code}] Sent to buffer: {'ON' if state else 'OFF'}")


def turn_on_dl_logic():
    def light_timer():
        if _settings['simulated']:
            set_led_state(True)
        else:
            import RPi.GPIO as GPIO
            GPIO.output(_settings['pin'], GPIO.HIGH)
        
        dl_callback(True, _settings['code'], _settings, _device_info)
        time.sleep(10)

        if _settings['simulated']:
            set_led_state(False)
        else:
            import RPi.GPIO as GPIO
            GPIO.output(_settings['pin'], GPIO.LOW)
            
        dl_callback(False, _settings['code'], _settings, _device_info)

    threading.Thread(target=light_timer, daemon=True).start()

def run_dl(settings, threads, stop_event, device_info):
        global _settings, _device_info
        _settings = settings
        _device_info = device_info
        print("Dl simulator started")
        if settings['simulated']:
            delay = settings['delay']
            code = settings['code']
            print("Starting {code} simulator")

            dl_thread = threading.Thread(
                target=run_dl_simulator, 
                args=(delay, lambda s, c: dl_callback(s, c, settings, device_info), stop_event, code)
            )
            dl_thread.start()
            threads.append(dl_thread)
        # else:
        #     import RPi.GPIO as GPIO
        #     import time
        #     pin = settings['pin']
        #     GPIO.setmode(GPIO.BCM)
        #     GPIO.setup(pin,GPIO.OUT)
        #     print("LED on")
        #     GPIO.output(pin,GPIO.HIGH)
        #     time.sleep(1)
        #     print("LED off")
        #     GPIO.output(pin,GPIO.LOW)
