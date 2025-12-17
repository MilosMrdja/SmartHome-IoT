import threading
import time
from simulators.dpir1 import run_dpir1_simulator
print_lock = threading.Lock()

def dpir1_callback(code):
    t = time.localtime()
    with print_lock:
        print("="*50)
        print(f"Code: {code}")
        print(f"Timestamp: {time.strftime('%H:%M:%S', t)}")
        print("Motion detected")

def run_dpir1(settings, threads, stop_event):
        if settings['simulated']:
            code = settings['code']
            print(f'Starting {code} sumilator')
            dpir1_thread = threading.Thread(target = run_dpir1_simulator, args=(2, dpir1_callback, stop_event, code))
            dpir1_thread.start()
            threads.append(dpir1_thread)
            print("DPIR1 sumilator started")
        else:
            print("Please implement DL - PI support")
            '''
            from sensors.dht import run_dht_loop, DHT
            print("Starting dht1 loop")
            dht = DHT(settings['pin'])
            dht1_thread = threading.Thread(target=run_dht_loop, args=(dht, 2, dht_callback, stop_event))
            dht1_thread.start()
            threads.append(dht1_thread)
            print("Dht1 loop started")
            '''