import json
import paho.mqtt.client as mqtt
from components.ir_component import ir_callback

def run_ir_remote_listener(device_info, mqtt_settings):
    def on_message(client, userdata, msg):
        data = json.loads(msg.payload.decode())
        if data.get("command") == "SIMULATE_IR":
            button = data.get("button")
            print(f"Remote simulation: Button {button} triggered via MQTT")
            dummy_settings = {'simulated': True, 'code': 'IR'}
            ir_callback(button, "IR", device_info, dummy_settings)

    client = mqtt.Client()
    client.on_message = on_message
    client.connect(mqtt_settings['broker_hostname'], mqtt_settings['port'])
    client.subscribe("commands/pi3/ir")
    client.loop_forever()