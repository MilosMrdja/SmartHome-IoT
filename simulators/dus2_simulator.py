import random
import time

def generate_dus2_distance(closed_distance=5, open_distance=100, noise=2, open_prob=0.1, close_prob=0.6):
    door_closed = True

    while True:
        if door_closed:
            
            if random.random() < open_prob:
                door_closed = False
        else:
            
            if random.random() < close_prob:
                door_closed = True

        base = closed_distance if door_closed else open_distance
        yield base + random.randint(-noise, noise)

def run_dus2_simulator(delay, callback, stop_event, code):
    for distance in generate_dus2_distance():
        time.sleep(delay)
        callback(distance, code)
        if stop_event.is_set():
            break