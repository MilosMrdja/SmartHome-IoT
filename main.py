import threading
import time
from config.load_settings import setup
from common.mqqt_sender import mqtt_batch_daemon

from components.dl_component import run_dl
from components.ds1_component import run_ds1
from components.dus1_component import run_dus1
from common.cli_listener import run_console_listener

from components.dl_component import run_dl
from components.dpir1_component import run_dpir1
from components.dms_component import run_dms
from components.db_component import run_db

try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
except:
    pass


if __name__ == "__main__":
    print('Starting app')
    settings = setup()
    device_info = settings['device_info']
    mqtt_settings = settings['mqtt']
    threads = []
    stop_event = threading.Event()

    # 1. Pokretanje MQTT Daemon niti
    mqtt_thread = threading.Thread(
        target=mqtt_batch_daemon, 
        args=(mqtt_settings, stop_event),
        daemon=True
    )
    mqtt_thread.start()
    threads.append(mqtt_thread)

    # 2. Pokretanje senzora
    run_dl(settings['DL'], threads, stop_event, device_info)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_event.set()
        GPIO.cleanup()

    '''try:
        dl_settings = settings['DL']
        ds1_settings = settings['DS1']
        dus1_settings = settings['DUS1']
        run_dl(dl_settings, threads, stop_event)
        run_ds1(ds1_settings, threads, stop_event)
        run_dus1(dus1_settings, threads, stop_event)
        dpir1_settings = settings['DPIR1']
        dms_settings = settings['DMS']
        db_settings = settings['DB']
        run_dpir1(dpir1_settings, threads, stop_event)
        run_dms(dms_settings, threads, stop_event)
        run_db(db_settings, threads, stop_event)

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
        for t in threads:       
            t.join() '''
