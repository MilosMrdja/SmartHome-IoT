import threading
import time
from simulators.dms_simulator import run_dms_simulator
from common.locks import print_lock


def dms_callback(code, key):
    t = time.localtime()
    with print_lock:
        print("=" * 50)
        print(f"Timestamp: {time.strftime('%H:%M:%S', t)}")
        print(f"Code: {code}")
        print(f"Key pressed: {key}")


def run_dms(settings, threads, stop_event):
    if settings['simulated']:
        code = settings['code']
        delay = settings.get('delay', 0.2)

        print(f"Starting {code} simulator")

        keypad_thread = threading.Thread(
            target=run_dms_simulator,
            args=(delay, dms_callback, stop_event, code),
            daemon=True
        )

        keypad_thread.start()
        threads.append(keypad_thread)

        print("DMS simulator started")
    else:
        pass
