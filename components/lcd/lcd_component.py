import threading
import time
from common.mqqt_sender import batch_queue
from simulators.lcd_simulator import run_lcd_simulator, set_lcd_state, get_lcd_state

def lcd_callback(line1, line2, code, settings, device_info):
    """Šalje trenutno stanje LCD-a u InfluxDB."""
    payload = {
        "measurement": "LCD_Display",
        "device_name": device_info['device_name'],
        "pi_id": device_info['pi_id'],
        "code": code,
        "line1": line1,
        "line2": line2,
        "simulated": settings['simulated']
    }
    batch_queue.put(payload)
    print(f"[{code}] LCD Influx Update: L1: '{line1}' | L2: '{line2}'")

def run_lcd_real(callback, stop_event, code, settings, device_info):
    """Logika za fizički LCD 1602 uređaj."""
    from .PCF8574 import PCF8574_GPIO
    from .Adafruit_LCD1602 import Adafruit_CharLCD

    address = 0x27
    try:
        mcp = PCF8574_GPIO(address)
    except:
        mcp = PCF8574_GPIO(0x3F)

    lcd = Adafruit_CharLCD(pin_rs=0, pin_e=2, pins_db=[4,5,6,7], GPIO=mcp)
    mcp.output(3,1)
    lcd.begin(16,2)

    last_l1, last_l2 = "", ""

    while not stop_event.is_set():
        line1, line2 = get_lcd_state()
        
        if line1 != last_l1 or line2 != last_l2:
            lcd.clear()
            lcd.setCursor(0,0)
            lcd.message(line1 + '\n')
            lcd.message(line2)
            
            callback(line1, line2, code, settings, device_info)
            
            last_l1, last_l2 = line1, line2
        
        time.sleep(0.5) 
    
    lcd.clear()

def run_lcd(settings, threads, stop_event, device_info):
    """Pokreće LCD komponentu."""
    code = settings['code']
    
    set_lcd_state("Waiting for", "DHT data...")

    if settings['simulated']:
        delay = settings['delay']

        lcd_thread = threading.Thread(
            target=run_lcd_simulator, 
            args=(delay, lambda l1, l2, c: lcd_callback(l1, l2, c, settings, device_info), stop_event, code)
        )
    else:
        lcd_thread = threading.Thread(
            target=run_lcd_real, 
            args=(lcd_callback, stop_event, code, settings, device_info)
        )

    lcd_thread.start()
    threads.append(lcd_thread)