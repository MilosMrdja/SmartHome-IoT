import time
import random

def generate_dl_state(initial_state=False, min_duration=2):
    state = initial_state
    counter = 0

    while True:
        
        if counter >= min_duration:
            if random.random() < 0.1: 
                state = not state
                counter = 0  
        counter += 1
        yield state

def run_dl_simulator(delay, callback, stop_event):
    for state in generate_dl_state():
        time.sleep(delay)
        callback(state)

        if stop_event.is_set():
            break