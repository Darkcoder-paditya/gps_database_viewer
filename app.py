import multiprocessing
import subprocess
from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
from pymongo import TEXT
from statistics import mean, median, mode
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
import plotly.graph_objects as go
from flask import render_template_string

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
    fig = go.Figure()

    # Add latitude trace
    fig.add_trace(go.Scatter(
        x=data.iloc[:, 0], y=data.iloc[:, 5], name='Latitude'))

    # Add longitude trace
    fig.add_trace(go.Scatter(
        x=data.iloc[:, 0], y=data.iloc[:, 6], name='Longitude'))

    # Add temperature trace
    fig.add_trace(go.Scatter(
        x=data.iloc[:, 0], y=data.iloc[:, 4], name='Temperature'))

    # Configure layout
    fig.update_layout(
        title='Robot Data Plots',
        xaxis_title='Time',
        yaxis_title='Value',
        hovermode='x',  # Enable x-axis hover
        template='plotly_white'  # Use a white background template
    )

    # Convert the plot to HTML
    plot_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

    return plot_html

@app.route('/data')
def get_data():
    connection = mysql.connector.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        database=MYSQL_DB,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD
    )

    # Fetch the latest data from the database
    query = "SELECT * FROM gps_data ORDER BY id DESC LIMIT 10"  
    data = pd.read_sql(query, connection)

    # Close the database connection
    connection.close()

    # Convert the data to JSON format and return
    data_json = data.to_json(orient='records')
    return data_json

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
    query = "SELECT * FROM gps_data ORDER BY id DESC LIMIT 10"
    data = pd.read_sql(query, connection)

    # Generate the plot
    plot_data = generate_plot(data)

    # Close the database connection
    connection.close()

    # Calculate statistics for the last 10 or 5 values (based on user input)
    # Default to 10 values if user input is not provided
    num_values = int(request.args.get('num_values', 10))
    last_values = data.tail(num_values)

    latitude_mean = round(mean(last_values['latitude']), 2)
    latitude_median = round(median(last_values['latitude']), 2)
    latitude_mode = round(mode(last_values['latitude']), 2)
    temperature_mean = round(mean(last_values['temperature']), 2)
    temperature_median = round(median(last_values['temperature']), 2)
    temperature_mode = round(mode(last_values['temperature']), 2)
    longitude_mean = round(mean(last_values['longitude']), 2)
    longitude_median = round(median(last_values['longitude']), 2)
    longitude_mode = round(mode(last_values['longitude']), 2)

    # Render the template with the updated plot and statistics
    return render_template('indexgr.html', plot_data=plot_data, latitude_mean=latitude_mean,
                           latitude_median=latitude_median, latitude_mode=latitude_mode,
                           temperature_mean=temperature_mean, temperature_median=temperature_median,
                           temperature_mode=temperature_mode, longitude_mean=longitude_mean,
                           longitude_median=longitude_median, longitude_mode=longitude_mode)


if __name__ == '__main__':
    subscriber_process = multiprocessing.Process(target=run_subscriber)
    subscriber_process.start()
    app.run()
    subscriber_process.join()
