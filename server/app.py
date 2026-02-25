import random
import threading
from flask import jsonify, request

from flask import Flask, render_template
import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import json
from flask_socketio import SocketIO

from config.config import MQTT_BROKER, MQTT_TOPIC,INFLUX_URL, INFLUX_TOKEN, INFLUX_ORG, INFLUX_BUCKET

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")


# InfluxDB setup
influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = influx_client.write_api(write_options=SYNCHRONOUS)

# VARs
mqtt_connected = False
people_count = 0
dht1_temp = 0
dht1_hum = 0
dht2_temp = 0
dht2_hum = 0
dht3_temp = 0
dht3_hum = 0
_4sd_current_value = "0100"
line1 = ""
line2 = ""
ds2 = "Zatvoreno"
ds1 = "Zatvoreno"
dl = "Iskljuceno"
db = "Iskljuceno"

HOME_PIN = "1234"
CURRENT_PIN = ""
ALARM_TRIGGERED = False # alarm radi
ALARM_ACTIVATED = False # alarm je spreman za rad


# --- MQTT CALLBACKS ---
def on_connect(client, userdata, flags, rc):
    global mqtt_connected
    if rc == 0:
        mqtt_connected = True
        print("Connected to MQTT Broker")
    else:
        mqtt_connected = False
        print("Connection failed")
    client.subscribe(MQTT_TOPIC)

def handle_vars(payload, client):
    if payload["measurement"] == "alarm_events":
        if payload["value"] == 1:
            alarm(client=client)
        else:
            alarm(client=client,state= False)
    elif payload['code'] == 'DPIR1' or payload['code'] == 'DPIR2':
        global people_count
        if payload['people_count'] is True:
            people_count += 1
        elif people_count is None:
            if people_count == 0:
                alarm(client=client)
        elif payload['people_count'] is False :
            if people_count > 0:
                people_count -= 1
            else:
                alarm(client=client)
    elif payload['code'] == 'DPIR3':
        if people_count == 0:
            alarm(client=client)

    elif payload['code'] == "DMS":
        global ALARM_ACTIVATED, ALARM_TRIGGERED, CURRENT_PIN
        if len(CURRENT_PIN)<4:
            CURRENT_PIN += str(payload['value'])

        if len(CURRENT_PIN) == 4:
            print(CURRENT_PIN)
            print(HOME_PIN)
            if CURRENT_PIN == HOME_PIN:
                if ALARM_TRIGGERED:
                    ALARM_TRIGGERED = False
                    alarm(client=client, state=False)

                elif not ALARM_ACTIVATED:
                    activate_system_with_delay()
                else:
                    ALARM_ACTIVATED = False
            else:
                activate_system()
                alarm(client=client)

            CURRENT_PIN = ""
            
    elif payload['code'] == "GSG":
        accel = payload['accel']
        gyro = payload['gyro']
        accel_threshold = 1.2
        gyro_threshold = 40.0
        
        significant_move = any(abs(a) > accel_threshold for a in accel[:2]) or abs(accel[2] - 1.0) > accel_threshold or any(abs(g) > gyro_threshold for g in gyro)

        print(payload)
        if significant_move:
            alarm(client=client, state = True)

def activate_system_with_delay():
    global ALARM_ACTIVATED
    threading.Timer(10, activate_system).start()

def activate_system():
    global ALARM_ACTIVATED
    ALARM_ACTIVATED = True
    print("ALARM WAS ACTIVATED")

def alarm(client, state = True):
    global ALARM_ACTIVATED
    global ALARM_TRIGGERED
    if not ALARM_ACTIVATED:
        return
    
    if state and not ALARM_TRIGGERED:
        command = {
            "command": "ON"   
        }
        ALARM_TRIGGERED = True
        client.publish("commands/alarm", json.dumps(command))
    elif not state and ALARM_TRIGGERED:
        command = {
            "command": "OFF"   
        }
        ALARM_TRIGGERED = False
        client.publish("commands/alarm", json.dumps(command))
        

def handle_val(payload):
    global dht1_temp, dht1_hum, dht2_temp, dht2_hum, dht3_temp, dht3_hum, _4sd_current_value, people_count, line1, line2, ds2, ds1, dl, db
    
    code = payload.get('code')
    
    if code == 'DHT1':
        dht1_temp, dht1_hum = payload['temperature'], payload['humidity']
    elif code == 'DHT2':
        dht2_temp, dht2_hum = payload['temperature'], payload['humidity']
    elif code == 'DHT3':
        dht3_temp, dht3_hum = payload['temperature'], payload['humidity']
    elif code == '4SD':
        _4sd_current_value = payload['value']
    elif code == 'DL':
        if payload['value'] == 1:
            dl = "Ukljuceno"
        else:
            dl = "Iskljuceno"
    elif code == 'DB':
        if payload['value'] == 1:
            db = "Ukljuceno"
        else:
            db = "Iskljuceno"
    elif code == "LCD":
        line1 = payload['line1']
        line2 = payload['line2']
    elif code == 'DS2':
        if payload['value'] == 1:
            ds2 = 'Otvoreno'
        else:
            ds2 = 'Zatvoreno'
    elif code == 'DS1':
        if payload['value'] == 1:
            ds1 = 'Otvoreno'
        else:
            ds1 = 'Zatvoreno'
    # Emitovanje preko socketa SVAKI put kad stigne podatak
    socketio.emit('update_data', {
        'dht1_temp': dht1_temp, 'dht1_hum': dht1_hum,
        'dht2_temp': dht2_temp, 'dht2_hum': dht2_hum,
        'dht3_temp': dht3_temp, 'dht3_hum': dht3_hum,
        '_4sd_current_value': _4sd_current_value,
        'people_count': people_count,
        'alarm_triggered': ALARM_TRIGGERED,
        'line1': line1,
        'line2':line2,
        'ds2':ds2,
        'ds1':ds1,
        'dl' : dl,
        'db':db
    })  
    if (payload['code'] == 'DHT3' or payload['code'] == 'DHT2' or payload['code'] == 'DHT1') and payload['measurement'] != "alarm_events":
        
        point = (
            Point(payload['measurement'])
            .tag("code", payload['code'])
            .tag("pi_id", payload['pi_id'])
            .tag("device_name", payload['device_name'])
            .tag("simulated", str(payload['simulated']))
            .field("temperature", payload['temperature'])
            .field("humidity", payload['humidity'])
        )
    elif payload['code'] == 'GSG' and payload['measurement'] != "alarm_events":
        point = (
            Point(payload['measurement'])
            .tag("code", payload['code'])
            .tag("pi_id", payload['pi_id'])
            .tag("device_name", payload['device_name'])
            .tag("simulated", str(payload['simulated']))
            .field("accel_x", payload['accel'][0])
            .field("accel_y", payload['accel'][1])
            .field("accel_z", payload['accel'][2])
            .field("gyro_x", payload['gyro'][0])
            .field("gyro_y", payload['gyro'][1])
            .field("gyro_z", payload['gyro'][2])
        )
    elif payload['code'] == 'LCD' and payload['measurement'] != "alarm_events":
        point = (
            Point(payload['measurement'])
            .tag("code", payload['code'])
            .tag("pi_id", payload['pi_id'])
            .tag("device_name", payload['device_name'])
            .tag("simulated", str(payload['simulated']))
            .field("line1", payload['line1'])
            .field("line2", payload['line2'])
        )

    else:

        point = (
            Point(payload['measurement'])
            .tag("code", payload['code'])
            .tag("pi_id", payload['pi_id'])
            .tag("device_name", payload['device_name'])
            .tag("simulated", str(payload.get('simulated', False)))
            .field("value", payload['value'])
        )

    return point

def on_message(client, userdata, msg):
    print("RAW MQTT:", msg.topic, msg.payload.decode())
    try:
        data_list = json.loads(msg.payload.decode())
        for data in data_list:

            # Proveri sva stanja
            handle_vars(data, client)

            # Napravi dobar point
            point = handle_val(data)

            write_api.write(bucket=INFLUX_BUCKET, record=point)
            print(f"Saved to Influx: {data}\n")
    except Exception as e:
        print("Error writing to Influx:", e)

# --- MQTT KLIJENT ---
mqtt_client = mqtt.Client(protocol=mqtt.MQTTv311)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

IR_BUTTONS = ["OK", "1", "2", "3", "4", "5", "6", "0"]

@app.route('/simulate-ir')
def simulate_ir():
    if mqtt_connected:
        button = random.choice(IR_BUTTONS)
        payload = {"command": "SIMULATE_IR", "button": button}
        # Šaljemo komandu direktno na temu koju PI3 sluša
        mqtt_client.publish("commands/pi3/ir", json.dumps(payload))
        return f"Poslata komanda za dugme: {button}", 200
    return "MQTT nije povezan", 500

@app.route('/update-display/<value>')
def update_display(value):
    if len(value) != 4 or not value.isdigit():
        return "Mora biti tačno 4 cifre", 400
    
    if mqtt_connected:
        payload = {"command": "SET_DISPLAY", "value": value}
        mqtt_client.publish("commands/pi2/4sd", json.dumps(payload))
        return f"Poslato na displej: {value}", 200
    return "MQTT nije povezan", 500

@app.route('/')
def index():
    status_text = "Online" if mqtt_connected else "Offline"
    status_color = "green" if mqtt_connected else "red"
    mqtt_info = "Povezan" if mqtt_connected else "Nije povezan"

    return render_template('index.html',
                           status=status_text,
                           curr_color=status_color,
                           mqtt_status=mqtt_info,
                           mqtt_broker=MQTT_BROKER,
                           people_count_pi1=people_count,
                           org_name=INFLUX_ORG,
                           _4sd_current_value_view=_4sd_current_value,
                           dht1_temp_view = dht1_temp,
                            dht1_hum_view = dht1_hum,
                            dht2_temp_view = dht2_temp,
                            dht2_hum_view = dht2_hum,
                            dht3_temp_view = dht3_temp,
                            dht3_hum_view = dht3_hum,
                           ALARM_TRIGGERED=ALARM_TRIGGERED)


@app.route('/toggle_alarm', methods=['POST'])
def toggle_alarm():
    global ALARM_TRIGGERED, CURRENT_PIN, ds1, ds2
    if ALARM_TRIGGERED:
        CURRENT_PIN = ""
        alarm(mqtt_client,state=False)
        print("ALARM DEAKTIVIRAN PREKO DASHBOARDA")
        ALARM_TRIGGERED = False
        return jsonify({"activated": False, "status": "detriggered"})
    return jsonify({"activated": False, "status": "no_trigger_active"})

def run_mqtt():
    mqtt_client.connect(MQTT_BROKER, 1883, 60)
    mqtt_client.loop_forever()


if __name__ == "__main__":

    thread = threading.Thread(target=run_mqtt)
    thread.daemon = True
    thread.start()

    app.run(debug=True, use_reloader=False, port=5000)
