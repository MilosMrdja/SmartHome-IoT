import threading
import time
from common.mqqt_sender import batch_queue
from simulators._4sd_simulator import set_4sd_state, get_4sd_state, run_4sd_simulator

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
    print(f"[{code}] InfluxDB Update: {value}")

def run_4sd_real(callback, stop_event, code, settings, device_info):
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    segments = settings['segment_pins']
    digits = settings['digit_pins']
    
    for s_pin in segments:
        GPIO.setup(s_pin, GPIO.OUT)
        GPIO.output(s_pin, 0)
    for d_pin in digits:
        GPIO.setup(d_pin, GPIO.OUT)
        GPIO.output(d_pin, 1)

    num = {
        ' ':(0,0,0,0,0,0,0), '0':(1,1,1,1,1,1,0), '1':(0,1,1,0,0,0,0),
        '2':(1,1,0,1,1,0,1), '3':(1,1,1,1,0,0,1), '4':(0,1,1,0,0,1,1),
        '5':(1,0,1,1,0,1,1), '6':(1,0,1,1,1,1,1), '7':(1,1,1,0,0,0,0),
        '8':(1,1,1,1,1,1,1), '9':(1,1,1,1,0,1,1)
    }

    try:
        while not stop_event.is_set():
            s = get_4sd_state() 
            
            for digit in range(4):
                if stop_event.is_set(): break
                
                for loop in range(0, 7):
                    GPIO.output(segments[loop], num[s[digit]][loop])
                
                if (int(time.time()) % 2 == 0) and (digit == 1):
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
    
    initial_value = settings.get('initial_value', "0100")
    set_4sd_state(initial_value)

    if settings['simulated']:
        seg_thread = threading.Thread(
            target=run_4sd_simulator, 
            args=(0.5, lambda v, c: _4sd_callback(v, c, settings, device_info), stop_event, code)
        )
    else:
        sim_thread = threading.Thread(
            target=run_4sd_simulator,
            args=(1.0, lambda v, c: _4sd_callback(v, c, settings, device_info), stop_event, code),
            daemon=True
        )
        sim_thread.start()
        threads.append(sim_thread)

        seg_thread = threading.Thread(
            target=run_4sd_real, 
            args=(_4sd_callback, stop_event, code, settings, device_info)
        )

    seg_thread.start()
    threads.append(seg_thread)