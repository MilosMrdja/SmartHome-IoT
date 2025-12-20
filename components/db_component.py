import threading
import time
from simulators.db_simulator import run_db_simulator
from common.locks import print_lock


def db_callback(state, code):
    t = time.localtime()
    with print_lock:
        print("=" * 50)
        print(f"Timestamp: {time.strftime('%H:%M:%S', t)}")
        print(f"Code: {code}")
        print("BUZZER HIGH" if state else "BUZZER LOW")


def run_db(settings, threads, stop_event):
    if settings['simulated']:
        print("Starting DB simulator")

        pitch = settings.get('pitch', 440)
        duration = settings.get('duration', 0.1)
        code = settings['code']


        db_thread = threading.Thread(
            target=run_db_simulator,
            args=(0.05, db_callback, stop_event, code, pitch, duration),
            daemon=True
        )

        db_thread.start()
        threads.append(db_thread)

        print("DB simulator started")
    else:
        pass
