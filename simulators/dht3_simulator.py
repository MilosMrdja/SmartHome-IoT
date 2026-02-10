import time
import random

def generate_dht3_values(initial_temp=25, initial_hum=20):
    temperature = initial_temp
    humidity = initial_hum

    while True:
        temperature += random.uniform(-0.5, 0.5)
        humidity += random.uniform(-1, 1)

        temperature = max(15, min(35, temperature))
        humidity = max(10, min(90, humidity))

        yield round(temperature, 2), round(humidity, 2)

def run_dht3_simulator(delay, callback, stop_event, code):
    for temp, hum in generate_dht3_values():
        if stop_event.is_set():
            break
            
        callback(code, temp, hum)
        
        time.sleep(delay)