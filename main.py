import threading
import time
from config.load_settings import setup
from components.dl_component import run_dl
from components.ds1_component import run_ds1
from components.dus1_component import run_dus1
from common.cli_listener import run_console_listener

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
        ds1_settings = settings['DS1']
        dus1_settings = settings['DUS1']
        run_dl(dl_settings, threads, stop_event)
        run_ds1(ds1_settings, threads, stop_event)
        run_dus1(dus1_settings, threads, stop_event)

        console_thread = threading.Thread(
            target=run_console_listener,
            args=(stop_event,),
            daemon=True
        )

        console_thread.start()
        threads.append(console_thread)

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print('Stopping app')
        for t in threads:
            stop_event.set()
