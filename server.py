from firebase_admin import credentials, firestore
from firebase_admin import db as firebase
from datetime import datetime, timezone
import firebase_admin
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import click
import traceback

@click.command()
@click.option("-h", "--host", default="localhost", help="MQTT broker address")
@click.option("-p", "--port", default=1883, help="MQTT broker port")
@click.option("-ka", "--keepalive", default=60, help="Connection keep alive")
@click.option("-t", "--topic", required=True, help="Device topic")
@click.option("-s", "--silent", default=True, help="Show traceback on error")
def run(**args):
    host = args.pop("host")
    port = args.pop("port")
    keepalive = args.pop("keepalive")
    topic = args.pop("topic")
    silent = args.pop("silent")

    cred = credentials.Certificate('credentials.json') 
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://blindstick-e0f8d-default-rtdb.asia-southeast1.firebasedatabase.app/"
    })
    parameter_reference = firebase.reference("device/parameters")
    setting_reference = firebase.reference("device/settings")
    firestore_db = firestore.client()
    trigger_collection = firestore_db.collection("triggers")

    def on_settings_change(event: firebase.Event):
        print(f"Setting listener triggered")
        settings = setting_reference.get()
        print(f"Got settings: {settings}")
        beep = settings.get("beep")
        fall_intensity_threshold = settings.get("fall_intensity_threshold")
        sound = settings.get("sound")
        msg = f"{int(beep)} {fall_intensity_threshold} {int(sound)}"
        publish.single("blindstick", msg, hostname=host)

    def on_connect(client, userdata, flags, reason_code, properties):
        print(f"Connected with result code: {reason_code}")
        client.subscribe(topic)

    def on_message(client, userdata, msg):
        # Payload format message: '{emergency} {fall} {obstacle} {water} {lat} {lon}'
        payload = bytes.decode(msg.payload)
        print(f"Received parameters: {payload}")

        try:
            data = payload.split()
            emergency = bool(float(data[0]))
            fall = bool(float(data[1]))
            obstacle = bool(float(data[2]))
            water = bool(float(data[3]))
            latitude = data[4]
            longitude = data[5]
            parameters = {
                "emergency": emergency,
                "fall": fall,
                "obstacle": obstacle,
                "water": water,
                "latitude": latitude,
                "longitude": longitude
            }
            parameter_reference.update(parameters)
            if emergency:
                trigger_collection.add({
                    "source": "emergency",
                    "created_at": datetime.now(tz=timezone.utc)
                })
            elif fall:
                trigger_collection.add({
                    "source": "fall",
                    "created_at": datetime.now(tz=timezone.utc)
                })
            elif obstacle:
                trigger_collection.add({
                    "source": "obstacle",
                    "created_at": datetime.now(tz=timezone.utc)
                })
            elif water:
                trigger_collection.add({
                    "source": "water",
                    "created_at": datetime.now(tz=timezone.utc)
                })
            print(f"Successfully updated data")
        except:
            print("Error occured")
            if not silent:
                print(traceback.format_exc())

    setting_listener = setting_reference.listen(on_settings_change)
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message
    mqttc.connect(host, port, keepalive)
    mqttc.loop_forever()


if __name__ == "__main__":
    run()