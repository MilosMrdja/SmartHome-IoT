import threading
import time
from components._4sd_component import run_4sd
from components.brgb_component import run_brgb
from components.btn_component import run_btn
from components.dht.dht1_component import run_dht1
from components.dht.dht2_component import run_dht2
from components.dht.dht3_component import run_dht3
from components.dpir2_component import run_dpir2
from components.dpir3_component import run_dpir3
from components.ds2_component import run_ds2
from components.dus2_component import run_dus2
from components.gsg.gsg_component import run_gsg
from components.ir_component import run_ir
from components.lcd.lcd_component import run_lcd
from components.webc_component import run_webc
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

    # 2. Pokretanje senzora za odredjeni PI
    if settings["device_info"]["pi_id"] == "PI1" :
        run_ds1(settings['DS1'], threads, stop_event, device_info) # vezbe 2
        run_dl(settings['DL'], threads, stop_event, device_info) # vezbe 1
        run_dus1(settings['DUS1'], threads, stop_event, device_info) # vezbe 3, jedan provodin 330, dva redna od 220
        run_db(settings['DB'], threads, stop_event, device_info) # vezbe 2
        run_dpir1(settings['DPIR1'], threads, stop_event, device_info) # vezbe 2
        run_dms(settings['DMS'], threads, stop_event, device_info) # vezbe 4
        # run_webc(settings['WEBC'],threads, stop_event, device_info)
        # export http_proxy="http://proxy.uns.ac.rs:8080"
        # export https_proxy="http://proxy.uns.ac.rs:8080"
        # mjpg_streamer -i "input_uvc.so" -o "output_http.so -p 8080 -w /usr/local/share/mjpg-streamer/www"
        # http://<raspberry_pi_ip>:8080/?action=stream
    elif settings["device_info"]["pi_id"] == "PI2":
        run_ds2(settings['DS2'], threads, stop_event, device_info)
        run_dus2(settings['DUS2'], threads, stop_event, device_info) # vezbe 3, jedan provodin 330, dva redna od 220
        run_dpir2(settings['DPIR2'], threads, stop_event, device_info) # vezbe 2
        run_4sd(settings['4SD'], threads, stop_event, device_info) # vezbe 4
        run_btn(settings['BTN'], threads, stop_event, device_info)
        run_dht3(settings['DHT3'], threads, stop_event, device_info) # vezbe 3
        run_gsg(settings['GSG'], threads, stop_event, device_info) # vezbe 6
    elif settings["device_info"]["pi_id"] == "PI3":
        run_dht1(settings['DHT1'], threads, stop_event, device_info) # vezbe 3
        run_dht2(settings['DHT2'], threads, stop_event, device_info) # vezbe 3
        run_ir(settings['IR'], threads, stop_event, device_info) # vezbe 5
        run_brgb(settings['BRGB'], threads, stop_event, device_info) # vezbe 4
        run_lcd(settings['LCD'], threads, stop_event, device_info) # vezbe 3
        run_dpir3(settings['DPIR3'], threads, stop_event, device_info) # vezbe 2



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
