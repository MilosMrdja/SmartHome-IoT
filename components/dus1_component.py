import threading
import time
from simulators.dus1_simulator import run_dus1_simulator
print_lock = threading.Lock()

def dus1_callback(distance):
    t = time.localtime()
    with print_lock:
        print("="*50)
        print(f"Timestamp: {time.strftime('%H:%M:%S', t)}")
        print(f"DUS1 | distance_cm = {distance}")

def run_dus1(settings, threads, stop_event):
        if settings['simulated']:
            print("Starting dus1 sumilator")
            dus1_thread = threading.Thread(target = run_dus1_simulator, args=(0.5, dus1_callback, stop_event))
            dus1_thread.start()
            threads.append(dus1_thread)
            print("DUS1 sumilator started")
        else:
            print("Please implement DUS1 - PI support")