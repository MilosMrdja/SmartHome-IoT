import time
import random

def generate_gsg_values():
    while True:
        accel = [
            round(random.uniform(-0.1, 0.1), 3),
            round(random.uniform(-0.1, 0.1), 3),
            round(random.uniform(0.9, 1.1), 3)
        ]
        gyro = [
            round(random.uniform(-0.5, 0.5), 3),
            round(random.uniform(-0.5, 0.5), 3),
            round(random.uniform(-0.5, 0.5), 3)
        ]
        yield accel, gyro

def run_gsg_simulator(delay, callback, stop_event, code):
    for accel, gyro in generate_gsg_values():
        time.sleep(delay)
        
        callback(code, accel, gyro)

        if stop_event.is_set():
            break