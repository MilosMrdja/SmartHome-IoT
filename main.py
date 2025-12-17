import threading
import time
from config.load_settings import setup
from components.dl import run_dl

# without Raspberry Pi GPIO, the import will fail
try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
except:
    pass


if __name__ == "__main__":
    print('Starting app')
    settings = setup()
    threads = []
    stop_event = threading.Event()
    try:
        dl_settings = settings['DL']
        run_dl(dl_settings, threads, stop_event)
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print('Stopping app')
        for t in threads:
            stop_event.set()
