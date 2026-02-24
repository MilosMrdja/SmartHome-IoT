import time
import threading

# 01:00 -> 60 minuta
current_value = "0100" 
display_lock = threading.Lock()
last_decrement_time = time.time()
force_callback_trigger = False

def set_4sd_state(value):
    with display_lock:
        global current_value, last_decrement_time, force_callback_trigger
        
        current_value = str(value).rjust(4, '0')[:4]
        
        last_decrement_time = time.time()
    
        force_callback_trigger = True
        print(f"DEBUG: Vrednost setovana na {current_value}, resetovan tajmer i aktiviran hitan upis.")
def get_4sd_state():
    with display_lock:
        return current_value

def run_4sd_simulator(delay, callback, stop_event, code):
    global last_decrement_time, current_value, force_callback_trigger
    last_influx_write = 0
    
    while not stop_event.is_set():
        now = time.time()

        # Provera za HITAN upis ili regularnih 60 sekundi
        # force_callback_trigger se aktivira unutar set_4sd_state
        if force_callback_trigger or (now - last_influx_write >= 60):
            current = get_4sd_state()
            callback(current, code)
            
            last_influx_write = now
            force_callback_trigger = False # Spusti zastavicu nakon izvršenja

        # Logika odbrojavanja (svakih 60 sekundi)
        if now - last_decrement_time >= 60:
            with display_lock:
                try:
                    hours = int(current_value[:2])
                    minutes = int(current_value[2:])
                    total_minutes = hours * 60 + minutes
                    
                    if total_minutes > 0:
                        total_minutes -= 1
                        current_value = f"{total_minutes // 60:02d}{total_minutes % 60:02d}"
                        print(f"[{code}] Timer smanjen na: {current_value}")
                    
                    last_decrement_time = now
                except ValueError:
                    pass
            
        time.sleep(delay)