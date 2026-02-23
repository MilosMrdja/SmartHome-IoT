import threading
import time
from common.mqqt_sender import batch_queue
from simulators.db_simulator import set_buzzer_state

is_alarm_active = False

def turn_alarm_on(device_info, settings):
    global is_alarm_active
    if not is_alarm_active:
        is_alarm_active = True
        set_buzzer_state(True)
        print(f"!!! ALARM WAS ACTIVATED!!!")
        
        payload = {
            "measurement": "alarm_events",
            "device_name": device_info['device_name'],
            "pi_id": device_info['pi_id'],
            "reason": settings["code"],
            "value": 1
        }
        print(payload)
        batch_queue.put(payload)

def turn_alarm_off(device_info):
    global is_alarm_active
    if is_alarm_active:
        is_alarm_active = False
        set_buzzer_state(False)
        print("ALARM WAS DEACTIVATED")
        
        payload = {
            "measurement": "alarm_events",
            "device_name": device_info['device_name'],
            "pi_id": device_info['pi_id'],
            "reason": "PIN_OR_WEB_DEACTIVATION",
            "value": 0 
        }
        batch_queue.put(payload)
