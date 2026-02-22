import random
import time

import random
import time


def generate_dus1_distance(
    far_distance=100,
    near_distance=5,
    step=15,
    noise=2,
    event_probability=0.05
):
    state = "idle"
    current_distance = far_distance

    while True:

        # POKRETANJE DOGAĐAJA
        if state == "idle" and random.random() < event_probability:
            state = random.choice(["entering", "exiting"])
            if state == "entering":
                current_distance = far_distance
            else:
                current_distance = near_distance

        # ULASAK (distance opada)
        elif state == "entering":
            current_distance -= step
            if current_distance <= near_distance:
                state = "idle"
                current_distance = far_distance

        # IZLAZAK (distance raste)
        elif state == "exiting":
            current_distance += step
            if current_distance >= far_distance:
                state = "idle"
                current_distance = far_distance

        yield current_distance + random.randint(-noise, noise)

def run_dus1_simulator(delay, callback, stop_event, code):
    for distance in generate_dus1_distance():
        time.sleep(delay)
        callback(distance, code)
        if stop_event.is_set():
            break