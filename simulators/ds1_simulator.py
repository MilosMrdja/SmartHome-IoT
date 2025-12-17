import random
import time

def generate_ds1_state(initial_state=True, min_duration=2):

    state = initial_state
    counter = 0
    while True:
        if counter >= min_duration:
            if random.random() > 0.2:
                state = not state
                counter = 0
        counter+=1
        yield state

def run_ds1_simulator(delay, callback, stop_event):
    for state in generate_ds1_state():
        time.sleep(delay)
        if state:
            callback()
        if stop_event.is_set():
            break