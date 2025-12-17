import threading
import time
from config.load_settings import setup
from components.dl import run_dl
from components.dpir1 import run_dpir1

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
        dpir1_settings = settings['DPIR1']
        run_dpir1(dpir1_settings, threads, stop_event, )
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print('Stopping app')
        for t in threads:
            stop_event.set()
        for t in threads:       
            t.join() 
