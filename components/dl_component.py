import threading
import time
from simulators.dl_simulator import run_dl_simulator
from common.locks import print_lock

def dl_callback(state):
    t = time.localtime()
    with print_lock:
        print("="*50)
        print(f"Timestamp: {time.strftime('%H:%M:%S', t)}")
        print("LED is ON" if state else "LED is OFF")

def run_dl(settings, threads, stop_event):
        if settings['simulated']:
            print("Starting dl simulator")
            dl_thread = threading.Thread(target = run_dl_simulator, args=(2, dl_callback, stop_event))
            dl_thread.start()
            threads.append(dl_thread)
            print("Dl simulator started")
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