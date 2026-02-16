import time
import threading

lcd_content = {
    "line1": "",
    "line2": ""
}
lcd_lock = threading.Lock()

def set_lcd_state(line1, line2):
    with lcd_lock:
        global lcd_content
        lcd_content["line1"] = line1
        lcd_content["line2"] = line2

def get_lcd_state():
    with lcd_lock:
        return lcd_content["line1"], lcd_content["line2"]

def run_lcd_simulator(delay, callback, stop_event, code):
    last_state = ("", "")
    while not stop_event.is_set():
        current_state = get_lcd_state()
        
        if current_state != last_state:
            callback(current_state[0], current_state[1], code)
            last_state = current_state
            
        time.sleep(delay)