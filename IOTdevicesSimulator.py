import paho.mqtt.client as mqtt
import json
import random
import time

# Callback to handle connection to the MQTT broker
def on_connect(client, userdata, flags, rc):
    print("Connected to broker with result: " + str(rc))
    # Subscribe to the topic zigbee2mqtt/# to receive messages from simulated IoT devices
    client.subscribe("zigbee2mqtt/#")

# Callback to handle received messages
def on_message(client, userdata, msg):
    print(f"Topic: {msg.topic}, Message: {msg.payload.decode('utf-8')}")
    try:
        # Decode the message as JSON and extract specific data
        decoded_message = json.loads(msg.payload.decode("utf-8"))
        if 'temperature' in decoded_message:
            temperature = decoded_message['temperature']
            print(f"Received temperature: {temperature}")
    except json.JSONDecodeError:
        print("Error decoding the message.")

# Function to publish simulated data from IoT sensors
def publish_simulated_data(client):
    while True:
        # Generate random data to simulate sensors
        temperature = random.uniform(20.0, 30.0)  # Simulated temperature
        humidity = random.uniform(40.0, 60.0)    # Simulated humidity
        
        # Publish the data to specific topics
        client.publish("zigbee2mqtt/temperature", json.dumps({"temperature": temperature}))
        client.publish("zigbee2mqtt/humidity", json.dumps({"humidity": humidity}))
        
        print(f"Published data: Temperature={temperature}, Humidity={humidity}")
        time.sleep(5)  # Wait 5 seconds before publishing again

# MQTT client configuration
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Connect to the MQTT broker (localhost for local testing)
client.connect("localhost", 1883)

# Start the loop in a separate thread to handle messages while publishing simulated data
client.loop_start()

try:
    publish_simulated_data(client)
except KeyboardInterrupt:
    print("Simulator stopped by user.")
finally:
    client.loop_stop()
    client.disconnect()
