import threading
import time
from common.mqqt_sender import batch_queue
from simulators.brgb_simulator import run_brgb_simulator

def brgb_callback(state, code, settings, device_info):
    payload = {
        "measurement": "Bedroom_RGB",
        "device_name": device_info['device_name'],
        "pi_id": device_info['pi_id'],
        "code": code,
        "value": state,
        "simulated": settings['simulated']
    }
    batch_queue.put(payload)
    
    print(f"[{code}] Sent to buffer: Bedroom RGB color is {state}")


def run_brgb_real(callback, stop_event, code, settings, device_info):
    import RPi.GPIO as GPIO
    
    RED_PIN = settings["red_pin"]
    GREEN_PIN = settings["green_pin"]
    BLUE_PIN = settings["blue_pin"]

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RED_PIN, GPIO.OUT)
    GPIO.setup(GREEN_PIN, GPIO.OUT)
    GPIO.setup(BLUE_PIN, GPIO.OUT)

    def turnOff():
        GPIO.output(RED_PIN, GPIO.LOW); GPIO.output(GREEN_PIN, GPIO.LOW); GPIO.output(BLUE_PIN, GPIO.LOW)
    def white():
        GPIO.output(RED_PIN, GPIO.HIGH); GPIO.output(GREEN_PIN, GPIO.HIGH); GPIO.output(BLUE_PIN, GPIO.HIGH)
    def red():
        GPIO.output(RED_PIN, GPIO.HIGH); GPIO.output(GREEN_PIN, GPIO.LOW); GPIO.output(BLUE_PIN, GPIO.LOW)
    def green():
        GPIO.output(RED_PIN, GPIO.LOW); GPIO.output(GREEN_PIN, GPIO.HIGH); GPIO.output(BLUE_PIN, GPIO.LOW)
    def blue():
        GPIO.output(RED_PIN, GPIO.LOW); GPIO.output(GREEN_PIN, GPIO.LOW); GPIO.output(BLUE_PIN, GPIO.HIGH)
    def yellow():
        GPIO.output(RED_PIN, GPIO.HIGH); GPIO.output(GREEN_PIN, GPIO.HIGH); GPIO.output(BLUE_PIN, GPIO.LOW)
    def purple():
        GPIO.output(RED_PIN, GPIO.HIGH); GPIO.output(GREEN_PIN, GPIO.LOW); GPIO.output(BLUE_PIN, GPIO.HIGH)
    def lightBlue():
        GPIO.output(RED_PIN, GPIO.LOW); GPIO.output(GREEN_PIN, GPIO.HIGH); GPIO.output(BLUE_PIN, GPIO.HIGH)

    sequence = [
        (turnOff, "OFF"), (white, "WHITE"), (red, "RED"), (green, "GREEN"),
        (blue, "BLUE"), (yellow, "YELLOW"), (purple, "PURPLE"), (lightBlue, "LIGHT_BLUE")
    ]

    try:
        while not stop_event.is_set():
            for action, name in sequence:
                if stop_event.is_set():
                    break
                action()
                callback(name, code, settings, device_info)
                time.sleep(1)
    finally:
        GPIO.cleanup()


def run_brgb(settings, threads, stop_event, device_info):
    code = settings['code']
    
    if settings['simulated']:
        delay = settings['delay']
        print(f"Starting {code} simulator")

        drgb_thread = threading.Thread(
            target=run_brgb_simulator, 
            args=(delay, lambda s, c: brgb_callback(s, c, settings, device_info), stop_event, code)
        )
    else:
        print(f"Starting {code} real sensor")

        drgb_thread = threading.Thread(
            target=run_brgb_real, 
            args=(brgb_callback, stop_event, code, settings, device_info)
        )

    drgb_thread.start()
    threads.append(drgb_thread)

    print(f"{code} started")