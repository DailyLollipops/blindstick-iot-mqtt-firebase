from firebase_admin import credentials, firestore
from firebase_admin import db as firebase
from datetime import datetime
from loguru import logger
import firebase_admin
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import click
import traceback
import pytz
import sys


log_base_format = '<green>{time}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> | <level>{message}</level> {extra}\n'
logger.add(
    f'app.log', 
    level="INFO", 
    format=log_base_format
)


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
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    parameter_reference = db.collection("parameters")
    current_parameter_document = parameter_reference.document("current")
    total_parameter_document = parameter_reference.document("total")
    setting_reference = db.collection("settings").document("current")

    current_parameters = current_parameter_document.get()
    if not current_parameters.exists:
        logger.error("Error in firestore schema: No document named current")
        raise Exception("Error in firestore schema: No document named current")

    total_parameters = total_parameter_document.get()
    if not total_parameters.exists:
        logger.error("Error in firestore schema: No document named total")
        raise Exception("Error in firestore schema: No document named total")

    def on_settings_change(doc_snapshot, changes, read_time):
        logger.info(f"Setting listener triggered")
        settings = doc_snapshot[-1].to_dict()
        logger.info(f"Current settings: {settings}")

    def on_connect(client, userdata, flags, reason_code, properties):
        logger.info(f"Connected with result code: {reason_code}")
        client.subscribe(topic)

    def on_message(client, userdata, msg):
        payload = bytes.decode(msg.payload)
        now = datetime.now(tz=pytz.timezone("Asia/Manila"))
        logger.info(f"Received parameters: {payload}")

        current_parameters = current_parameter_document.get().to_dict()
        current_parameters.pop("updated_at", "")
        total_parameters = total_parameter_document.get().to_dict()

        try:
            data = payload.split()
            obstacle1= bool(float(data[0]))
            obstacle2= bool(float(data[1]))
            obstacle3= bool(float(data[2]))
            obstacle4= bool(float(data[3]))
            water = bool(float(data[4]))
            fall = bool(float(data[5]))
            emergency = bool(float(data[6]))
            power = bool(float(data[7]))
            stop = bool(float(data[8]))
            parameters = {
                "obstacle1": obstacle1,
                "obstacle2": obstacle2,
                "obstacle3": obstacle3,
                "obstacle4": obstacle4,
                "water": water,
                "fall": fall,
                "emergency": emergency,
                "power": power,
                "stop": stop
            }

            if current_parameters != parameters:
                logger.info("Current parameters changed")
                parameters["updated_at"] = now
                current_parameter_document.update(parameters)
                logger.info(f"New paraemters: {parameters}")
            else:
                logger.info("Current parameters did not changed")
                return

            temp_total = total_parameters.copy()
            if any([obstacle1, obstacle2, obstacle3, obstacle4]):
                temp_total["obstacle"] += 1
            elif water:
                temp_total["water"] += 1
            elif fall:
                temp_total["fall"] += 1
            elif emergency:
                temp_total["emergency"] += 1
            
            if total_parameters != temp_total:
                logger.info("Total parameters count changed")
                temp_total["updated_at"] = now
                total_parameter_document.update(temp_total)
                logger.info(f"Total parameters: {temp_total}")
            else:
                logger.info("Total parameters count did not changed")
        except Exception as e:
            logger.warning(f"Error occurred: {e}")
            if not silent:
                logger.error(traceback.format_exc())

    setting_listener = setting_reference.on_snapshot(on_settings_change)
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message
    mqttc.connect(host, port, keepalive)
    mqttc.loop_forever()


if __name__ == "__main__":
    run()