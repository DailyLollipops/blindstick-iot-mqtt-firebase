import paho.mqtt.publish as publish
import click
import traceback

@click.command()
@click.option("-h", "--host", required=True, help="MQTT broker address")
@click.option("-t", "--topic", required=True, help="Topic to publish to")
@click.option("-p", "--payload", required=True, help="Payload to send")
@click.option("-s", "--silent", default=True, help="Show traceback on error")
def run(host, topic, payload, silent):
    print(f"Sending {payload} to {host} on topic {topic}")
    try:
        publish.single(topic, payload, hostname=host)
        print("Success")
    except:
        print("Failed.")
        if not silent:
            print(traceback.format_exc())

if __name__ == "__main__":
    run()
