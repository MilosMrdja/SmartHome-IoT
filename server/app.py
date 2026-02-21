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

def on_message(client, userdata, msg):
    print("RAW MQTT:", msg.topic, msg.payload.decode())
    try:
        data_list = json.loads(msg.payload.decode())
        for data in data_list:
            # Kreiraj InfluxDB Point
            point = (
                Point(data['measurement'])
                .tag("code", data['code'])
                .tag("pi_id", data['pi_id'])
                .tag("device_name", data['device_name'])
                .tag("simulated", str(data['simulated']))
                .field("value", data['value']) #TODO izmeniti za dms
            )
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
                           color=status_color,
                           mqtt_status=mqtt_info,
                           mqtt_broker=MQTT_BROKER,
                           org_name=INFLUX_ORG)


def run_mqtt():
    mqtt_client.connect(MQTT_BROKER, 1883, 60)
    mqtt_client.loop_forever()


if __name__ == "__main__":

    thread = threading.Thread(target=run_mqtt)
    thread.daemon = True
    thread.start()

    app.run(debug=True, port=5000)
