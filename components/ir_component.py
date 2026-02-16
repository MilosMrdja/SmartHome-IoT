import threading
import time
from common.locks import print_lock
from common.mqqt_sender import batch_queue
from simulators.ir_simulator import run_ir_simulator, BUTTON_CODES, BUTTON_NAMES

def ir_callback(button, code, device_info, settings):
    payload = {
        "measurement": "Bedroom_Infrared",
        "device_name": device_info['device_name'],
        "pi_id": device_info['pi_id'],
        "code": code,
        "value": button,
        "simulated": settings['simulated'] 
    }
    batch_queue.put(payload) 
    print(f"[{code}] Sent to buffer: IR Button {button} detected")


def get_binary(pin, stop_event):
    import RPi.GPIO as GPIO
    from datetime import datetime
    
    num1s = 0
    binary = 1
    command = []
    previousValue = 0
    
    while GPIO.input(pin):
        if stop_event.is_set(): return None
        time.sleep(0.0001)
        
    startTime = datetime.now()
    while not stop_event.is_set():
        value = GPIO.input(pin)
        if previousValue != value:
            now = datetime.now()
            pulseTime = now - startTime
            startTime = now
            command.append((previousValue, pulseTime.microseconds))
        
        if value: num1s += 1
        else: num1s = 0
        
        if num1s > 10000: break
        previousValue = value
        
    for (typ, tme) in command:
        if typ == 1:
            if tme > 1000: binary = binary * 10 + 1
            else: binary *= 10
            
    if len(str(binary)) > 34:
        binary = int(str(binary)[:34])
    return binary

def run_ir_real(pin, callback, stop_event, device_info, settings):
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.IN)
    
    with print_lock:
        print(f"Real IR sensor started on pin {pin}")

    while not stop_event.is_set():
        binary_val = get_binary(pin, stop_event)
        if binary_val is None or binary_val == 1:
            continue
        
        try:
            inData = hex(int(str(binary_val), 2))
            
            found = False
            for i in range(len(BUTTON_CODES)):
                if hex(BUTTON_CODES[i]) == inData:
                    callback(BUTTON_NAMES[i], settings['code'], device_info, settings)
                    found = True
                    break
            
            if not found:
                with print_lock:
                    print(f"Unknown IR code: {inData}")
                    
        except Exception as e:
            with print_lock:
                print(f"IR Error: {e}")

def run_ir(settings, threads, stop_event, device_info):
    if settings['simulated']:
        delay = settings["delay"]
        code = settings['code']
        print(f'Starting {code} simulator')
        ir_thread = threading.Thread(
            target=run_ir_simulator, 
            args=(delay, ir_callback, stop_event, code, device_info, settings)
        )        
    else:
        pin = settings['pin']
        code = settings['code']
        print(f'Starting {code} real sensor')
        ir_thread = threading.Thread(
            target=run_ir_real, 
            args=(pin, ir_callback, stop_event, device_info, settings)
        )

    ir_thread.start()
    threads.append(ir_thread)