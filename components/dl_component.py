import threading
import time
from simulators.dl_simulator import run_dl_simulator
from common.locks import print_lock

def dl_callback(state, code):
    t = time.localtime()
    with print_lock:
        print("="*50)
        print(f"Timestamp: {time.strftime('%H:%M:%S', t)}")
        print(f"Code: {code}")
        print("LED is ON" if state else "LED is OFF")

def run_dl(settings, threads, stop_event):
        if settings['simulated']:
            print("Starting dl simulator")
            delay = settings['delay']
            code = settings['code']
            dl_thread = threading.Thread(target = run_dl_simulator, args=(delay, dl_callback, stop_event, code))
            dl_thread.start()
            threads.append(dl_thread)
            print("Dl simulator started")
        else:
            pass