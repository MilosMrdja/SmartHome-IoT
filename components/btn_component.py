import threading
import time
from common.locks import print_lock
from common.mqqt_sender import batch_queue
from simulators._4sd_simulator import get_4sd_state, set_4sd_state
from simulators.btn_simulator import run_btn_simulator

def btn_callback(code, device_info, settings):
    current_s = get_4sd_state()
    
    try:
        hours = int(current_s[:2])
        minutes = int(current_s[2:])
        
        total_minutes = (hours * 60) + minutes + 2
        
        if total_minutes > 5999: 
            total_minutes = 5999
            
        new_hours = total_minutes // 60
        new_mins = total_minutes % 60
        
        new_value = f"{new_hours:02d}{new_mins:02d}"
        
        set_4sd_state(new_value)
        print(f"[{code}] Dugme pritisnuto! Dodata 2 minuta. Novo stanje: {new_value}")
        
    except Exception as e:
        print(f"[{code}] Greška pri ažuriranju tajmera: {e}")

    # Slanje eventa u InfluxDB (da ostane trag da je dugme pritisnuto)
    payload = {
        "measurement": "kitchen button",
        "device_name": device_info['device_name'],
        "pi_id": device_info['pi_id'],
        "code": code,
        "value": 1,
        "simulated": settings['simulated']
    }
    batch_queue.put(payload)

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