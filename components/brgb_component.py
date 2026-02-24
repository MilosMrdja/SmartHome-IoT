import threading
import time
from common.mqqt_sender import batch_queue
from simulators.brgb_simulator import run_brgb_simulator

brgb_status = {
    "is_on": False,
    "current_color": "OFF"
}
status_lock = threading.Lock()

def update_brgb_state(turn_on=None, color=None):
    with status_lock:
        if turn_on is not None:
            brgb_status["is_on"] = turn_on
        if color is not None:
            brgb_status["current_color"] = color

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
        GPIO.output(RED_PIN, GPIO.LOW)
        GPIO.output(GREEN_PIN, GPIO.LOW)
        GPIO.output(BLUE_PIN, GPIO.LOW)
    def white():
        GPIO.output(RED_PIN, GPIO.HIGH)
        GPIO.output(GREEN_PIN, GPIO.HIGH)
        GPIO.output(BLUE_PIN, GPIO.HIGH)
    def red():
        GPIO.output(RED_PIN, GPIO.HIGH)
        GPIO.output(GREEN_PIN, GPIO.LOW)
        GPIO.output(BLUE_PIN, GPIO.LOW)
    def green():
        GPIO.output(RED_PIN, GPIO.LOW)
        GPIO.output(GREEN_PIN, GPIO.HIGH)
        GPIO.output(BLUE_PIN, GPIO.LOW)
    def blue():
        GPIO.output(RED_PIN, GPIO.LOW)
        GPIO.output(GREEN_PIN, GPIO.LOW)
        GPIO.output(BLUE_PIN, GPIO.HIGH)
    def yellow():
        GPIO.output(RED_PIN, GPIO.HIGH)
        GPIO.output(GREEN_PIN, GPIO.HIGH)
        GPIO.output(BLUE_PIN, GPIO.LOW)
    def purple():
        GPIO.output(RED_PIN, GPIO.HIGH)
        GPIO.output(GREEN_PIN, GPIO.LOW)
        GPIO.output(BLUE_PIN, GPIO.HIGH)
    def lightBlue():
        GPIO.output(RED_PIN, GPIO.LOW)
        GPIO.output(GREEN_PIN, GPIO.HIGH)
        GPIO.output(BLUE_PIN, GPIO.HIGH)

    actions = {
        "OFF": turnOff, "WHITE": white, "RED": red, "GREEN": green,
        "BLUE": blue, "YELLOW": yellow, "PURPLE": purple, "LIGHT_BLUE": lightBlue
    }

    last_applied_color = ""

    try:
        while not stop_event.is_set():
            with status_lock:
                on = brgb_status["is_on"]
                color = brgb_status["current_color"]

            target_color = color if on else "OFF"

            # Primeni boju samo ako se promenila da ne bismo stalno pisali po GPIO
            if target_color != last_applied_color:
                actions[target_color]()
                callback(target_color, code, settings, device_info)
                last_applied_color = target_color
            
            time.sleep(0.1)
    finally:
        GPIO.cleanup()

def run_brgb_simulator_temp(delay, callback, stop_event, code):
    """
    Reaktivni simulator koji prati brgb_status i šalje podatke 
    samo kada dođe do promene stanja.
    """
    last_applied_color = None
    
    while not stop_event.is_set():
        # Čitanje trenutnog ciljanog stanja pod lock-om
        with status_lock:
            on = brgb_status["is_on"]
            color = brgb_status["current_color"]

        # Određujemo boju: ako je isključeno, uvek je "OFF"
        target_color = color if on else "OFF"

        # Ako se boja promenila u odnosu na poslednju poslatu
        if target_color != last_applied_color:
            callback(target_color, code)
            last_applied_color = target_color
        
        # Mala pauza da nit ne "pojede" procesor (ne mora delay iz settingsa)
        time.sleep(0.1)

def run_brgb(settings, threads, stop_event, device_info):
    code = settings['code']
    
    if settings['simulated']:
        delay = settings['delay']
        print(f"Starting {code} simulator")

        drgb_thread = threading.Thread(
            target=run_brgb_simulator_temp, 
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