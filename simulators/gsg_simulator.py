import time
import random

def generate_gsg_values():
    while True:
        if random.random() < 0.95:
            accel = [round(random.uniform(-0.05, 0.05), 3), 
                     round(random.uniform(-0.05, 0.05), 3), 
                     round(random.uniform(0.95, 1.05), 3)]
            gyro = [round(random.uniform(-0.1, 0.1), 3) for _ in range(3)]
        else:
            accel = [round(random.uniform(0.5, 1.5), 3) for _ in range(3)]
            gyro = [round(random.uniform(20, 50), 3) for _ in range(3)]
        
        yield accel, gyro

def run_gsg_simulator(delay, callback, stop_event, code):
    for accel, gyro in generate_gsg_values():
        if stop_event.is_set():
            break
        
        callback(code, accel, gyro)
        time.sleep(delay)