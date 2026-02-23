import time
import threading

buzzer_state = False
state_lock = threading.Lock()


def set_buzzer_state(value: bool):
    global buzzer_state
    with state_lock:
        buzzer_state = value


def get_buzzer_state():
    with state_lock:
        return buzzer_state


def run_db_simulator(loop_delay, callback, stop_event, code, pitch, duration):
    last_state = False
    
    while not stop_event.is_set():
        current_state = get_buzzer_state()
        
        if current_state != last_state:
            callback(current_state, code)
            last_state = current_state

        if current_state:
            period = 1.0 / pitch
            half_period = period / 2
            cycles = int(duration * pitch)
            
            for _ in range(cycles):
                time.sleep(half_period)
                time.sleep(half_period)
