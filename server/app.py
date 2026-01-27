from flask import Flask
import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import json

app = Flask(__name__)

# --- KONFIGURACIJA ---
MQTT_BROKER = "192.168.0.102"   # LAN IP Windows mašine ili 'mqtt5' ako je Docker
MQTT_TOPIC = "iot/+/batch"

INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "yK-78RS83HLW-SoRZhcxe432D3kDIku2o8h8IYlnX3bGfVVXnE8rk0RShe0SbgkD9lOwlBJ0W7ZXenN4nwAqvQ=="
INFLUX_ORG = "docs"
INFLUX_BUCKET = "home"

# InfluxDB setup
influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = influx_client.write_api(write_options=SYNCHRONOUS)

# --- MQTT CALLBACKS ---
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker with result code", rc)
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    print("RAW MQTT:", msg.topic, msg.payload.decode())
    try:
        data_list = json.loads(msg.payload.decode())
        for data in data_list:
            # Kreiraj InfluxDB Point
            point = (
                Point(data['measurement'])
                .tag("pi_id", data['pi_id'])
                .tag("device_name", data['device_name'])
                .tag("simulated", str(data['simulated']))
                .field("value", float(data['value']))
            )
            write_api.write(bucket=INFLUX_BUCKET, record=point)
            print(f"Saved to Influx: {data}")
    except Exception as e:
        print("Error writing to Influx:", e)

# --- MQTT KLIJENT ---
mqtt_client = mqtt.Client(protocol=mqtt.MQTTv311)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect(MQTT_BROKER, 1883, 60)
mqtt_client.loop_forever()
