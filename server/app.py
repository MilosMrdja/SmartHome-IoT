import threading

from flask import Flask, render_template
import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import json
from config.config import MQTT_BROKER, MQTT_TOPIC,INFLUX_URL, INFLUX_TOKEN, INFLUX_ORG, INFLUX_BUCKET

app = Flask(__name__)



# InfluxDB setup
influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = influx_client.write_api(write_options=SYNCHRONOUS)

# VAR
mqtt_connected = False
people_count = 0

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
    if payload['code'] == 'DPIR1' or payload['code'] == 'DPIR2':
        global people_count
        if payload['people_count']:
            people_count += 1
        elif people_count is None:
            pass
        else:
            if people_count > 0:
                people_count -= 1
            else:
                alarm(client=client)
    elif payload['code'] == 'DPIR3':
        if people_count == 0:
            alarm(client=client)

def alarm(client, state = True):
    if state:
        command = {
            "command": "ON"   
        }
        client.publish("commands/alarm", json.dumps(command))
    else:
        command = {
            "command": "OFF"   
        }
        client.publish("commands/alarm", json.dumps(command))
        

def handle_val(payload):
    if payload['code'] == 'DHT3' or payload['code'] == 'DHT2' or payload['code'] == 'DHT1':
        point = (
            Point(payload['measurement'])
            .tag("code", payload['code'])
            .tag("pi_id", payload['pi_id'])
            .tag("device_name", payload['device_name'])
            .tag("simulated", str(payload['simulated']))
            .field("temperature", payload['temperature'])
            .field("humidity", payload['humidity'])
        )
    elif payload['code'] == 'GSG':
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
    elif payload['code'] == 'LCD':
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
            .tag("simulated", str(payload['simulated']))
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
                           org_name=INFLUX_ORG)


def run_mqtt():
    mqtt_client.connect(MQTT_BROKER, 1883, 60)
    mqtt_client.loop_forever()


if __name__ == "__main__":

    thread = threading.Thread(target=run_mqtt)
    thread.daemon = True
    thread.start()

    app.run(debug=True, port=5000)
