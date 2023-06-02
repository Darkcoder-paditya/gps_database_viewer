
    
    # app.py
import multiprocessing, subprocess
from flask import Flask, render_template, jsonify
from pymongo import MongoClient
from pymongo import TEXT
import mysql.connector


app = Flask(__name__, static_folder='static')

# MongoDB configuration
MONGO_HOST = 'mongodb+srv://pa:prashant@cluster0.5b0djvj.mongodb.net/'
MONGO_PORT = 27017
MONGO_DB = 'gps_data'
COLLECTION_NAME = 'gps_messages'
USERNAME = 'pa'
PASSWORD = 'prashant'

# Mysql
MYSQL_HOST = 'localhost'
MYSQL_PORT = 3306
MYSQL_DB = 'gps_data'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'root'

# Connect to MongoDB
mongo_client = MongoClient(MONGO_HOST, MONGO_PORT, username=USERNAME, password=PASSWORD)
db = mongo_client[MONGO_DB]
collection = db[COLLECTION_NAME]

# Connect to MySQL


@app.route('/delete', methods=['DELETE'])
def delete_data():
    try:
        result = collection.delete_many({})
        deleted_count = result.deleted_count
        return jsonify({'message': 'Data deleted successfully', 'deleted_count': deleted_count}), 200
    except Exception as e:
        return jsonify({'message': 'Failed to delete data', 'error': str(e)}), 500

# 
@app.route('/')
@app.route('/<robot_ids>')
def display_data_route(robot_ids=None):
    mysql_connection = mysql.connector.connect(
    host=MYSQL_HOST,
    port=MYSQL_PORT,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DB
    )
    mysql_cursor = mysql_connection.cursor()
    if mysql_connection.is_connected():
        print("Connected to MySQL")
    else:
        print("Failed to connect to MySQL")
    if robot_ids:
        robot_id_list = robot_ids.split(',')

        # Prepare the SQL query
        query = "SELECT * FROM gps_data WHERE robot_id IN (%s)" % (','.join(['%s'] * len(robot_id_list)))

        # Execute the SQL query
        mysql_cursor.execute(query, tuple(robot_id_list))

        # Fetch the data from MySQL
        columns = [column[0] for column in mysql_cursor.description]
        data = [dict(zip(columns, row)) for row in mysql_cursor.fetchall()]
    else:
        # Fetch all data from MySQL
        mysql_cursor.execute("SELECT * FROM gps_data")
        columns = [column[0] for column in mysql_cursor.description]
        data = [dict(zip(columns, row)) for row in mysql_cursor.fetchall()]

    return render_template('./index.html', data=data)

def run_subscriber():
    subprocess.run(['python', './subscribe.py'])

if __name__ == '__main__':
    subscriber_process = multiprocessing.Process(target=run_subscriber)
    subscriber_process.start()
    app.run()
    
    subscriber_process.join()
    