import threading
import time
from simulators.dus1_simulator import run_dus1_simulator
from common.locks import print_lock

def dus1_callback(distance, code):
    t = time.localtime()
    with print_lock:
        print("="*50)
        print(f"Timestamp: {time.strftime('%H:%M:%S', t)}")
        print(f"Code: {code}")
        print(f"DUS1 | distance_cm = {distance}")

def run_dus1(settings, threads, stop_event):
        if settings['simulated']:
            print("Starting dus1 sumilator")
            delay = settings['delay']
            code = settings['code']
            dus1_thread = threading.Thread(target = run_dus1_simulator, args=(delay, dus1_callback, stop_event, code))
            dus1_thread.start()
            threads.append(dus1_thread)
            print("DUS1 sumilator started")
        else:
            pass