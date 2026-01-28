import threading
import time
from simulators.dms_simulator import run_dms_simulator
from common.locks import print_lock
from common.mqqt_sender import batch_queue


def dms_callback(code, key, settings, device_info):
    payload = {
        "measurement": "Door Membrane Switch 1",
        "device_name": device_info['device_name'],
        "pi_id": device_info['pi_id'],
        "code": code,
        "value": key,
        "simulated": settings['simulated'] 
    }
    batch_queue.put(payload) 
    print(f"[{code}] Sent to buffer: {key} key pressed")


def run_dms(settings, threads, stop_event, device_info):
    if settings['simulated']:
        code = settings['code']
        delay = settings.get('delay', 0.2)
        print(f"Starting {code} simulator")
        keypad_thread = threading.Thread(
            target=run_dms_simulator,
            args=(delay, lambda c, k: dms_callback(c, k, settings, device_info), stop_event, code),
            daemon=True
        )
        keypad_thread.start()
        threads.append(keypad_thread)
    else:
        def keypad_loop(settings, device_info, stop_event):
            import RPi.GPIO as GPIO
            
            R_PINS = settings['r_pins'] # Očekuje listu tipa [25, 8, 7, 1]
            C_PINS = settings['c_pins'] # Očekuje listu tipa [12, 16, 20, 21]
            code = settings['code']

            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)

            for pin in R_PINS:
                GPIO.setup(pin, GPIO.OUT)
            for pin in C_PINS:
                GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

            def readLine(line_pin, characters):
                GPIO.output(line_pin, GPIO.HIGH)
                for idx, col_pin in enumerate(C_PINS):
                    if GPIO.input(col_pin) == 1:
                        key = characters[idx]
                        dms_callback(code, key, settings, device_info)
                        while GPIO.input(col_pin) == 1:
                            time.sleep(0.05)
                GPIO.output(line_pin, GPIO.LOW)

            try:
                while not stop_event.is_set():
                    readLine(R_PINS[0], ["1","2","3","A"])
                    readLine(R_PINS[1], ["4","5","6","B"])
                    readLine(R_PINS[2], ["7","8","9","C"])
                    readLine(R_PINS[3], ["*","0","#","D"])
                    time.sleep(0.1)
            finally:
                GPIO.cleanup()

        dms_thread = threading.Thread(target=keypad_loop, args=(settings, device_info, stop_event), daemon=True)
        dms_thread.start()
        threads.append(dms_thread)
        print(f"DMS real sensor started on code: {settings['code']}")