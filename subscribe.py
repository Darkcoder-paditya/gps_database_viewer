import paho.mqtt.client as mqtt
import json
from pymongo import MongoClient
import mysql.connector

# MySQL configuration
MYSQL_HOST = 'localhost'
MYSQL_PORT = 3306
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'root'
MYSQL_DB = 'gps_data'

# Establish MySQL connection
mysql_connection = mysql.connector.connect(
    host=MYSQL_HOST,
    port=MYSQL_PORT,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DB
)
mysql_cursor = mysql_connection.cursor()


MQTTBROKER = 'test.mosquitto.org'
PORT = 1883

# MongoDB configuration
MONGO_HOST = 'mongodb+srv://pa:prashant@cluster0.5b0djvj.mongodb.net/'
MONGO_PORT = 27017
MONGO_DB = 'gps_data'
COLLECTION_NAME = 'gps_messages'
USERNAME = 'pa'
PASSWORD = 'prashant'

# Connect to MongoDB
try:
    mongo_client = MongoClient(MONGO_HOST, MONGO_PORT, username=USERNAME, password=PASSWORD)
    db = mongo_client[MONGO_DB]
    collection = db[COLLECTION_NAME]
    print("Connected to MongoDB")
except Exception as e:
    print("Failed to connect to MongoDB:", str(e))

serial_number = 0

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("gps_data")

def on_disconnect(client, userdata, rc):
    print("Disconnected with result code " + str(rc))

def on_message(client, userdata, msg):
    global serial_number
    serial_number += 1

    print(MQTTBROKER + ': <' + msg.topic + "> : " +  str(msg.payload.decode()))

    message = msg.payload.decode()
    topic = msg.topic

    try:
        message_data = json.loads(message)
        if isinstance(message_data, dict):
            latitude = message_data.get("latitude", 0.0)
            longitude = message_data.get("longitude", 0.0)
            temperature = message_data.get("temperature", 0.0)
            robid = message_data.get("robid", 0.0)
        else:
            raise ValueError("Invalid message format: message_data is not a dictionary")
    except (json.JSONDecodeError, ValueError) as e:

        print("Failed to parse message as JSON:", str(e))
        return

    document = {
        "serial_number": serial_number,
        "topic": topic,
        "temperature": temperature,
        "latitude": latitude,
        "longitude": longitude,
        "robid":robid
    }

    insert_query = "INSERT INTO gps_data (serial_number, robot_id, topic, temperature, latitude, longitude) VALUES (%s, %s, %s, %s, %s, %s)"
    insert_values = (serial_number, robid, topic, temperature, latitude, longitude)
    mysql_cursor.execute(insert_query, insert_values)
    mysql_connection.commit()

    collection.insert_one(document)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect
client.connect(MQTTBROKER, PORT)
client.loop_forever()
mysql_cursor.close()
mysql_connection.close()
