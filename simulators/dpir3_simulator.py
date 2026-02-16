import time
import random

def generate_dpir3_state(initial_state=False):
    state = initial_state

    while True:
        if random.random() < 0.5:
            state = not state

        yield state

def run_dpir3_simulator(delay, callback, stop_event, code):
    for state in generate_dpir3_state():
        time.sleep(delay)
        if state:
            callback(code)

        if stop_event.is_set():
            break