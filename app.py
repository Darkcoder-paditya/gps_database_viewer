import multiprocessing
import subprocess
from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
from pymongo import TEXT
import mysql.connector
import matplotlib.pyplot as plt
import csv
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np


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


@app.route('/delete', methods=['DELETE'])
def delete_data():
    try:
        mysql_connection = mysql.connector.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB
        )
        mysql_cursor = mysql_connection.cursor()
        mysql_cursor.execute("DELETE FROM gps_data")
        mysql_connection.commit()
        mysql_cursor.close()
        mysql_connection.close()

        # Check if the deletion was successful in MySQL
        if mysql_cursor.rowcount > 0:
            print("Data deleted from MySQL")
        else:
            print("No data deleted from MySQL")

        result = collection.delete_many({})
        deleted_count = result.deleted_count
        return jsonify({'message': 'Data deleted successfully', 'deleted_count': deleted_count}), 200
    except Exception as e:
        return jsonify({'message': 'Failed to delete data', 'error': str(e)}), 500


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
    # if request.path == '/graphs':
        # return redirect(url_for('index'))
    mysql_cursor = mysql_connection.cursor()
    if robot_ids:
        robot_id_list = robot_ids.split(',')

        query = "SELECT * FROM gps_data WHERE robot_id IN (%s)" % (','.join(['%s'] * len(robot_id_list)))

        mysql_cursor.execute(query, tuple(robot_id_list))

        columns = [column[0] for column in mysql_cursor.description]
        data = [dict(zip(columns, row)) for row in mysql_cursor.fetchall()]
    else:
        mysql_cursor.execute("SELECT * FROM gps_data")
        columns = [column[0] for column in mysql_cursor.description]
        data = [dict(zip(columns, row)) for row in mysql_cursor.fetchall()]

    return render_template('./index.html', data=data)

def run_subscriber():
    subprocess.run(['python', './subscribe.py'])


def generate_plot(data):
    # print(data)
    fig, axs = plt.subplots(3, 1, figsize=(18.9, 12))
    plt.subplots_adjust(hspace=0.5)

    # Plotting latitude
    axs[0].plot(data.iloc[:, 0], data.iloc[:, 5])
    axs[0].set_xlabel('Time')
    axs[0].set_ylabel('Latitude')
    axs[0].set_title('Time vs Latitude')

    # Plotting longitude
    axs[1].plot(data.iloc[:, 0], data.iloc[:, 6])
    axs[1].set_xlabel('Time')
    axs[1].set_ylabel('Longitude')
    axs[1].set_title('Time vs Longitude')

    # Plotting temperature
    axs[2].plot(data.iloc[:, 0], data.iloc[:, 4])
    axs[2].set_xlabel('Time')
    axs[2].set_ylabel('Temperature')
    axs[2].set_title('Time vs Temperature')

    # Save the plot to a BytesIO object
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plot_data = base64.b64encode(buffer.getvalue()).decode()
    buffer.close()

    return plot_data

@app.route('/graphs')
def index():
    connection = mysql.connector.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        database=MYSQL_DB,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD
    )

    # Fetch data from the database
    query = "SELECT * FROM gps_data"
    data = pd.read_sql(query, connection)

    # Generate the plot
    plot_data = generate_plot(data)

    # Close the database connection
    connection.close()


    return render_template('indexgr.html', plot_data=plot_data, target='_self')





if __name__ == '__main__':
    subscriber_process = multiprocessing.Process(target=run_subscriber)
    subscriber_process.start()
    app.run()
    subscriber_process.join()