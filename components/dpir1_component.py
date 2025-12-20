import threading
import time
from simulators.dpir1_simulator import run_dpir1_simulator
from common.locks import print_lock

def dpir1_callback(code):
    t = time.localtime()
    with print_lock:
        print("="*50)
        print(f"Timestamp: {time.strftime('%H:%M:%S', t)}")
        print(f"Code: {code}")
        print("Motion detected")

def run_dpir1(settings, threads, stop_event):
        if settings['simulated']:
            code = settings['code']
            print(f'Starting {code} simulator')
            dpir1_thread = threading.Thread(target = run_dpir1_simulator, args=(2, dpir1_callback, stop_event, code))
            dpir1_thread.start()
            threads.append(dpir1_thread)
            print("DPIR1 simulator started")
        else:
            pass