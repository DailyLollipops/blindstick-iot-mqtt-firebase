from firebase_admin import credentials, firestore, messaging
import firebase_admin
import paho.mqtt.client as mqtt
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
    app = firebase_admin.initialize_app(cred)
    db = firestore.client()
    device_collection = db.collection("devices")

    def on_connect(client, userdata, flags, reason_code, properties):
        print(f"Connected with result code: {reason_code}")
        client.subscribe(topic)

    def on_message(client, userdata, msg):
        # Payload format message: '{id} {balance} {obstacle} {water} {lat} {lon}'
        payload = bytes.decode(msg.payload)
        print(f"Received: {payload}")

        try:
            data = payload.split()
            device_id = data[0]
            balance = bool(float(data[1]))
            obstacle = bool(float(data[2]))
            water = float(data[3])
            latitude = data[4]
            longitude = data[5]
            document = device_collection.document(device_id)
            document_data = {
                "balance": balance,
                "obstacle": obstacle,
                "water": water,
                "latitude": latitude,
                "longitude": longitude
            }
            document.update(document_data)
            print(f"Successfully updated data on device ID: {device_id}")
        except:
            print("Error occured")
            if not silent:
                print(traceback.format_exc())

    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message
    mqttc.connect(host, port, keepalive)
    mqttc.loop_forever()

if __name__ == "__main__":
    run()