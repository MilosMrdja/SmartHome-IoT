import threading
import time
from simulators.ds1_simulator import run_ds1_simulator
from common.locks import print_lock

def ds1_callback(code):
    t = time.localtime()
    with print_lock:
        print("="*50)
        print(f"Timestamp: {time.strftime('%H:%M:%S', t)}")
        print(f"Code: {code}")
        print(f"DS1 - button_pressed")

def run_ds1(settings, threads, stop_event):
        if settings['simulated']:
            print("Starting ds1 sumilator")
            delay = settings['delay']
            code = settings['code']
            ds1_thread = threading.Thread(target = run_ds1_simulator, args=(delay, ds1_callback, stop_event, code))
            ds1_thread.start()
            threads.append(ds1_thread)
            print("DS1 sumilator started")
        else:
            pass