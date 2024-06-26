# python 3.11

import random
import time

from paho.mqtt import client as mqtt_client

broker = 'mosquitto'
port = 1883
# Generate a Client ID with the publish prefix.
client_id = f'publish-{random.randint(0, 1000)}'


# username = 'emqx'
# password = 'public'

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    print(f"Trying to connect to {broker}:{port}")
    client.connect(broker, port)
    return client


def publish(client, msg, topic):
    msg_count = 1
    while True:
        time.sleep(1)
        result = client.publish(topic, msg)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")
        msg_count += 1
        if msg_count > 5:
            break




def run():
    client = connect_mqtt()
    client.loop_start()
    publish(client)
    client.loop_stop()
