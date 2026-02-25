import threading
import time
from common.locks import print_lock
from common.mqqt_sender import batch_queue
from simulators.gsg_simulator import run_gsg_simulator
from scripts.alarm import turn_alarm_on

def gsg_callback(code, device_info, settings, accel, gyro):
    payload = {
        "measurement": "gyroscope",
        "device_name": device_info['device_name'],
        "pi_id": device_info['pi_id'],
        "code": code,
        "accel": accel,
        "gyro": gyro,
        "simulated": settings['simulated'] 
    }
    print(payload)
    batch_queue.put(payload) 


def real_gsg_loop(settings, stop_event, device_info):
    from .MPU6050 import MPU6050
    mpu = MPU6050()
    mpu.dmp_initialize()
    code = settings['code']
    
    while not stop_event.is_set():
        accel_raw = mpu.get_acceleration()
        gyro_raw = mpu.get_rotation()
        
        accel = [round(a / 16384.0, 3) for a in accel_raw]
        gyro = [round(g / 131.0, 3) for g in gyro_raw]
        
        gsg_callback(code, device_info, settings, accel, gyro)
        time.sleep(settings.get('delay', 0.5))


def run_gsg(settings, threads, stop_event, device_info):
    if settings['simulated']:
        code = settings['code']
        gsg_thread = threading.Thread(
            target=run_gsg_simulator, 
            args=(
                settings['delay'], 
                lambda c, a, g: gsg_callback(c, device_info, settings, a, g), 
                stop_event, 
                code
            )
        )
        gsg_thread.start()
        threads.append(gsg_thread)
    else:
        gsg_thread = threading.Thread(target=real_gsg_loop, args=(settings, stop_event, device_info))
        gsg_thread.start()
        threads.append(gsg_thread)