import time
import random

def generate_dl_state(initial_state=False):
    state = initial_state

    while True:
        if random.random() < 0.1:  # 10%
            state = not state

        yield state

def run_dl_simulator(delay, callback, stop_event):
    for state in generate_dl_state():
        time.sleep(delay)
        callback(state)

        if stop_event.is_set():
            break