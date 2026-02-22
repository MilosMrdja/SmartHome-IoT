import threading
import time
from simulators.ds1_simulator import run_ds1_simulator
from scripts.alarm import turn_alarm_on, turn_alarm_off
from common.locks import print_lock
from common.mqqt_sender import batch_queue

active_timers = {}
    
def ds_hardware_callback(pin, callback, code, device_info, settings):
    import RPi.GPIO as GPIO
    device_name = device_info['device_name']
    is_open = GPIO.input(pin) == GPIO.HIGH

    if is_open:
        if device_name not in active_timers:
            t = threading.Timer(5.0, turn_alarm_on, args=(device_info, settings))
            active_timers[device_name] = t
            t.start()
        callback(code, device_info, settings, 1, alarm_active=False)
    else:
        if device_name in active_timers:
            active_timers[device_name].cancel()
            del active_timers[device_name]
        turn_alarm_off(device_info)
        callback(code, device_info, settings, 0, alarm_active=False)
    
def ds1_callback(code, device_info, settings, value):
    payload = {
        "measurement": "button door 1",
        "device_name": device_info['device_name'],
        "pi_id": device_info['pi_id'],
        "code": code,
        "value": value,
        "simulated": settings['simulated']
    }
    batch_queue.put(payload)
    print(payload)
    print(f"[{code}] Sent to buffer: button pressed")

def run_ds1(settings, threads, stop_event, device_info):
        if settings['simulated']:
            delay = settings['delay']
            code = settings['code']
            print("Starting {code} simulator")
            ds1_thread = threading.Thread(target = run_ds1_simulator, args=(delay, lambda c, d, s, v: ds1_callback(c, d, s, v), stop_event, code, device_info, settings))
            ds1_thread.start()
            threads.append(ds1_thread)
            print("DS1 sumilator started")
        else:
            import RPi.GPIO as GPIO
            port_btn = settings['pin']
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(port_btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            # GPIO.add_event_detect(port_btn, GPIO.RISING, callback=lambda c: ds1_callback(settings['code'], device_info, settings), bouncetime = 100)
            GPIO.add_event_detect(port_btn, GPIO.BOTH, 
                              callback=lambda x: ds_hardware_callback(port_btn, ds1_callback, code, device_info, settings), 
                              bouncetime=50)