import random
import time

def generate_brgb_state():
    colors = ["OFF", "RED", "GREEN", "BLUE", "WHITE", "YELLOW", "PURPLE", "LIGHT_BLUE"]
    while True:
        yield random.choice(colors)

def run_brgb_simulator(delay, callback, stop_event, code):
    for state in generate_brgb_state():
        if stop_event.is_set():
            break
        
        callback(state, code)
        time.sleep(delay)