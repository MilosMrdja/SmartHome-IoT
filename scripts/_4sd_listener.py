import json
import paho.mqtt.client as mqtt
from components._4sd_component import set_4sd_state

# Dodaj device_info ovde
def run_display_listener(device_info, mqtt_settings):
    def on_message(client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode())
            if data.get("command") == "SET_DISPLAY":
                new_value = data.get("value")
                print(f"[{device_info['device_name']}] Set 4SD to: {new_value}")
                set_4sd_state(new_value)
        except Exception as e:
            print(f"Error in display listener: {e}")

    client = mqtt.Client()
    client.on_message = on_message
    client.connect(mqtt_settings['broker_hostname'], mqtt_settings['port'])
    client.subscribe("commands/pi2/4sd")
    client.loop_forever()