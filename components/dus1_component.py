import threading
import time
from simulators.dus1_simulator import run_dus1_simulator
from common.locks import print_lock
from common.mqqt_sender import batch_queue
from scripts.people_counter import update_distance


def dus1_callback(distance, code, device_info, settings):
    payload = {
        "measurement": "door ultrasonic 1",
        "device_name": device_info['device_name'],
        "pi_id": device_info['pi_id'],
        "code": code,
        "value": distance,
        "simulated": settings['simulated'] 
    }
    batch_queue.put(payload) 
    update_distance(sensor_id=1, distance=distance)
    print(f"[{code}] Sent to buffer: ultrasonic sensor detected distance")

def run_dus1(settings, threads, stop_event, device_info):
    if settings['simulated']:
        delay = settings['delay']
        code = settings['code']
        print(f'Starting {code} simulator')
        dus1_thread = threading.Thread(target=run_dus1_simulator, args=(delay, lambda d, c: dus1_callback(d, c, device_info, settings), stop_event, code))          
        dus1_thread.start()
        threads.append(dus1_thread)
    else:
        def sensor_loop(settings, device_info, stop_event):
            import RPi.GPIO as GPIO
            GPIO.setmode(GPIO.BCM)
            TRIG_PIN = settings['trig_pin']
            ECHO_PIN = settings['echo_pin']
            code = settings['code']
            max_iter = settings['max_iter']

            GPIO.setup(TRIG_PIN, GPIO.OUT)
            GPIO.setup(ECHO_PIN, GPIO.IN)

            try:
                while not stop_event.is_set():
                    GPIO.output(TRIG_PIN, False)
                    time.sleep(0.2)
                    GPIO.output(TRIG_PIN, True)
                    time.sleep(0.00001)
                    GPIO.output(TRIG_PIN, False)

                    pulse_start_time = time.time()
                    pulse_end_time = time.time()

                    iter = 0
                    while GPIO.input(ECHO_PIN) == 0:
                        if iter > max_iter or stop_event.is_set(): break
                        pulse_start_time = time.time()
                        iter += 1

                    iter = 0
                    while GPIO.input(ECHO_PIN) == 1:
                        if iter > max_iter or stop_event.is_set(): break
                        pulse_end_time = time.time()
                        iter += 1

                    if iter <= max_iter:
                        pulse_duration = pulse_end_time - pulse_start_time
                        distance = (pulse_duration * 34300) / 2
                        
                        dus1_callback(distance, code, device_info, settings)
                    
                    time.sleep(settings.get('delay', 1))
            finally:
                GPIO.cleanup()

        dus1_thread = threading.Thread(target=sensor_loop, args=(settings, device_info, stop_event))
        dus1_thread.start()
        threads.append(dus1_thread)
        print(f"DUS1 real sensor started on code: {settings['code']}")