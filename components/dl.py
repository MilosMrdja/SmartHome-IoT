import threading
import time
from simulators.dl import run_dl_simulator

def dht_callback(state):
    t = time.localtime()
    print("="*50)
    print(f"Timestamp: {time.strftime('%H:%M:%S', t)}")
    print("LED is ON" if state else "LED is OFF")

def run_dl(settings, threads, stop_event):
        if settings['simulated']:
            print("Starting dl sumilator")
            # 60 sec, because door state changes state rarely
            dl_thread = threading.Thread(target = run_dl_simulator, args=(60, dht_callback, stop_event))
            dl_thread.start()
            threads.append(dl_thread)
            print("Dl sumilator started")
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