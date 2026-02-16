import threading
import time
from common.mqqt_sender import batch_queue
from simulators._4sd_simulator import *

def _4sd_callback(value, code, settings, device_info):
    payload = {
        "measurement": "7-Segment Display",
        "device_name": device_info['device_name'],
        "pi_id": device_info['pi_id'],
        "code": code,
        "value": value,
        "simulated": settings['simulated']
    }
    batch_queue.put(payload)
    print(f"[{code}] Display updated: {value}")

def run_4sd_real(callback, stop_event, code, settings, device_info):
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    segments = settings['segment_pins']
    digits = settings['digit_pins']
    
    for segment in segments:
        GPIO.setup(segment, GPIO.OUT)
        GPIO.output(segment, 0)
    for digit in digits:
        GPIO.setup(digit, GPIO.OUT)
        GPIO.output(digit, 1)

    num = {
        ' ':(0,0,0,0,0,0,0), '0':(1,1,1,1,1,1,0), '1':(0,1,1,0,0,0,0),
        '2':(1,1,0,1,1,0,1), '3':(1,1,1,1,0,0,1), '4':(0,1,1,0,0,1,1),
        '5':(1,0,1,1,0,1,1), '6':(1,0,1,1,1,1,1), '7':(1,1,1,0,0,0,0),
        '8':(1,1,1,1,1,1,1), '9':(1,1,1,1,0,1,1)
    }

    try:
        last_callback_time = 0
        while not stop_event.is_set():
            current_time = time.ctime()
            n = current_time[11:13] + current_time[14:16]
            s = str(n).rjust(4)
            
            if time.time() - last_callback_time > 5:
                set_4sd_state(s)
                callback(s, code, settings, device_info)
                last_callback_time = time.time()

            for digit in range(4):
                if stop_event.is_set(): break
                
                for loop in range(0, 7):
                    GPIO.output(segments[loop], num[s[digit]][loop])
                
                if (int(time.ctime()[18:19]) % 2 == 0) and (digit == 1):
                    GPIO.output(segments[7], 1)
                else:
                    GPIO.output(segments[7], 0)
                
                GPIO.output(digits[digit], 0)
                time.sleep(0.001)
                GPIO.output(digits[digit], 1)
    finally:
        GPIO.cleanup()

def run_4sd(settings, threads, stop_event, device_info):
    code = settings['code']
    
    if settings['simulated']:
        delay = settings.get('delay', 1)
        def simulated_logic():
            while not stop_event.is_set():
                n = time.ctime()[11:13] + time.ctime()[14:16]
                set_4sd_state(n)
                time.sleep(1)

        logic_thread = threading.Thread(target=simulated_logic)
        logic_thread.start()
        threads.append(logic_thread)

        seg_thread = threading.Thread(
            target=run_4sd_simulator, 
            args=(delay, lambda v, c: _4sd_callback(v, c, settings, device_info), stop_event, code)
        )
    else:
        seg_thread = threading.Thread(
            target=run_4sd_real, 
            args=(_4sd_callback, stop_event, code, settings, device_info)
        )

    seg_thread.start()
    threads.append(seg_thread)