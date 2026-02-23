import random
import time
from scripts.alarm import turn_alarm_on, turn_alarm_off

def generate_ds1_state():
    while True:
        is_open = random.random() < 0.6
        if is_open:
            duration = random.randint(2, 8)
            for _ in range(duration):
                yield True
        else:
            yield False

def run_ds1_simulator(delay, callback, stop_event, code, device_info, settings):
    open_start_time = None
    last_state = None

    for is_open in generate_ds1_state():
        if stop_event.is_set():
            break
        
        current_time = time.time()
        
        if is_open:
            if open_start_time is None:
                open_start_time = current_time
            
            if current_time - open_start_time > 5:
                turn_alarm_on(device_info=device_info, settings=settings)
        else:
            open_start_time = None
            turn_alarm_off(device_info=device_info)

        if is_open != last_state:
            callback(code, device_info, settings, 1 if is_open else 0)
            last_state = is_open
            print(f"[{code}] State changed to: {'OPEN' if is_open else 'CLOSED'}")

        time.sleep(delay)