# MQTT Firebase Server for Blindstick IoT project

A publisher based implementation of MQTT to update firestore database collection for the Blindstick IoT project

## Setup

1. Setup a MQTT broker (e.g. Mosquitto) which you can connect to
2. Create and setup a firebase project
3. Download a service account from that project and rename it as `credentials.json`
4. Install requirements with `pip install -r requirements.txt`

### Running

To run the server, make sure the MQTT broker is up and running, then run:

```bash
python server.py -t blindstick
```

where the `-t` argument is the topic subscribed on by the blindstick devices

### Testing

You can run the publish script by emulating the data sent by the blindstick devices using

```bash
python publish.py -h localhost -t blindstick -p "1 0 1 16.1 121.34221 77.4343"
```

where:

- -h = mqtt broker address
- -t = topic subscribed
- -p = payload - Payload format message: '{id} {balance} {obstacle} {water} {lat} {lon}'
