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
from plotly.subplots import make_subplots
import numpy as np
import plotly.graph_objects as go
from flask import render_template_string
from flask import Flask, render_template
# import mysql.connector
# import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import mpld3


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

quality_cutoffs = {
    'quality_1': 20,
    'quality_2': 30,
    'quality_3': 50
}


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
        mysql_cursor.execute("ALTER TABLE gps_data AUTO_INCREMENT = 1")
        mysql_connection.commit()
        mysql_cursor.close()
        mysql_connection.close()

        if mysql_cursor.rowcount > 0:
            print("Data deleted from MySQL")
        else:
            print("No data deleted from MySQL")

        deleted_count = 100
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

        query = "SELECT * FROM gps_data WHERE robot_id IN (%s)" % (
            ','.join(['%s'] * len(robot_id_list)))

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

    fig.add_trace(go.Scatter(
        x=data.iloc[:, 0], y=data.iloc[:, 7], name='Quality 1'))

    fig.add_trace(go.Scatter(
        x=data.iloc[:, 0], y=data.iloc[:, 8], name='Quality 2'))

    fig.add_trace(go.Scatter(
        x=data.iloc[:, 0], y=data.iloc[:, 9], name='Quality 3'))

    fig.add_trace(go.Scatter(
        x=data.iloc[:, 0], y=data.iloc[:, 4], name='Temperature'))

    fig.update_layout(
        title='Sensor Data vs Time',
        xaxis_title='Time',
        yaxis_title='Values in SI Unit',
        hovermode='closest',
        template='plotly_white',
        height=600,
        width=1150,
        paper_bgcolor='rgb(22, 40, 88)',
        plot_bgcolor='rgb(22, 40, 88)',
        font_family="Courier New",
        font_color="rgb(138, 228, 255)",
        title_font_family="Times New Roman",
        title_font_color="rgb(138, 228, 255)",
        font_size=20,
    )

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

    query = "SELECT * FROM gps_data ORDER BY id DESC LIMIT 50"
    data = pd.read_sql(query, connection)

    connection.close()

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
    cursor = connection.cursor()
    cursor.execute('SELECT robot_id, AVG(temperature) AS average_temperature FROM gps_data GROUP BY robot_id UNION SELECT \'Global Avg\' AS robot_id, AVG(temperature) AS average_temperature FROM gps_data  order by robot_id ASC ')
    temperature_results = cursor.fetchall()

    cursor.execute('SELECT robot_id, AVG(quality_1) AS average_quality_1 FROM gps_data GROUP BY robot_id UNION SELECT \'Global Avg\' AS robot_id, AVG(quality_1) AS average_quality_1 FROM gps_data order by robot_id ASC')
    quality_1_results = cursor.fetchall()

    cursor.execute('SELECT robot_id, AVG(quality_2) AS average_quality_2 FROM gps_data GROUP BY robot_id UNION SELECT \'Global Avg\' AS robot_id, AVG(quality_2) AS average_quality_2 FROM gps_data order by robot_id ASC')
    quality_2_results = cursor.fetchall()

    cursor.execute('SELECT robot_id, AVG(quality_3) AS average_quality_3 FROM gps_data GROUP BY robot_id UNION SELECT \'Global Avg\' AS robot_id, AVG(quality_3) AS average_quality_3 FROM gps_data order by robot_id ASC')
    quality_3_results = cursor.fetchall()

    temperature_x = []
    temperature_y = []
    for row in temperature_results:
        temperature_x.append(row[0])
        temperature_y.append(row[1])

    quality_1_x = []
    quality_1_y = []
    for row in quality_1_results:
        quality_1_x.append(row[0])
        quality_1_y.append(row[1])

    quality_2_x = []
    quality_2_y = []
    for row in quality_2_results:
        quality_2_x.append(row[0])
        quality_2_y.append(row[1])

    quality_3_x = []
    quality_3_y = []
    for row in quality_3_results:
        quality_3_x.append(row[0])
        quality_3_y.append(row[1])
    # bfig = go.Figure()

    # bfig.add_trace(go.Bar(x=temperature_x, y=temperature_y, name='Average Temperature'))
    # bfig.add_trace(go.Bar(x=quality_1_x, y=quality_1_y, name='Average Quality 1'))
    # bfig.add_trace(go.Bar(x=quality_2_x, y=quality_2_y, name='Average Quality 2'))
    # bfig.add_trace(go.Bar(x=quality_3_x, y=quality_3_y, name='Average Quality 3'))

    # bfig.update_layout(
    #     barmode='group',
    #     xaxis_title='Robot IDs',
    #     yaxis_title='Average Value',
    #     title='Average Values for Temperature and Quality Metrics'
    # )

    # bgraph_data = bfig.to_html(full_html=False)
    bfig = make_subplots(rows=3, cols=1, subplot_titles=[
        # 'Average Temperature',
        'Average Quality 1',
        'Average Quality 2',
        'Average Quality 3'
    ])

    # bfig.add_trace(go.Bar(x=temperature_x, y=temperature_y, name='Average Temperature'), row=1, col=1)
    bfig.add_trace(go.Bar(x=quality_1_x, y=quality_1_y,
                   name='Average Quality 1'), row=1, col=1)
    bfig.add_trace(go.Bar(x=quality_2_x, y=quality_2_y,
                   name='Average Quality 2'), row=2, col=1)
    bfig.add_trace(go.Bar(x=quality_3_x, y=quality_3_y,
                   name='Average Quality 3'), row=3, col=1)

    bfig.update_layout(
        height=950,
        width=635,
        title_text='Average Values for Quality Metrics',
        showlegend=False,
        paper_bgcolor='rgb(22, 40, 88)',
        plot_bgcolor='rgb(22, 40, 88)',
        font_family="Courier New",
        font_size=20,

        font_color="rgb(138, 228, 255)",
        title_font_family="Times New Roman",
        title_font_color="rgb(138, 228, 255)",
        # title_font_size=20,
        title={

            'font': {'size': 20}
        }
        # legend_title_font_color="rgb(138, 228, 255)",
        # legend_title_font_size=20,
    )
    bargraph_data = bfig.to_html(full_html=False)
    # Close the database connection
    # connection.close()

    # _________________________________________________________________________________________

    fig, axs = plt.subplots(1, 3, figsize=(17, 6), subplot_kw={'aspect': 'equal'})

    for i, quality in enumerate(quality_cutoffs.keys()):
        ax = axs[i]
        ax.set_title(quality.capitalize(), fontsize=20, color= '#8ae4ff', fontweight='bold')

        cursor.execute(f"SELECT robot_id, {quality} FROM gps_data ORDER BY robot_id ASC")
        rows = cursor.fetchall()

        filtered_values = [row for row in rows if row[1] > quality_cutoffs[quality]]

        unique_robot_ids = list(set(row[0] for row in filtered_values))
        robot_counts = [sum(1 for row in filtered_values if row[0] == robot_id) for robot_id in unique_robot_ids]

        num_robot_ids = len(unique_robot_ids)
        radii = [0.3 + i * 0.2 for i in range(num_robot_ids)]  # Increase the radius values for larger circles
        labels = unique_robot_ids

        legend_labels = []
        legend_handles = []
        legend_notations = []

        colors = plt.cm.get_cmap('tab20')(range(num_robot_ids))

        wedge_width = 1 / num_robot_ids

        for radius, label, count, color in zip(radii, labels, robot_counts, colors):
            if count > 0:
                percentage = (count / len(filtered_values)) * 100
                notation = f"{percentage:.1f}%"
                wedgeprops = {'width': wedge_width, 'edgecolor': 'w'}
                wedges, _ = ax.pie([count, len(filtered_values) - count], labels=['', ''],
                                    radius=radius, colors=[color, 'lightgray'],
                                    wedgeprops=wedgeprops)
                legend_labels.append(label)
                legend_handles.append(Patch(facecolor=color, edgecolor='w'))
                legend_notations.append(notation)

        # Create the legend for the current subplot
        legend = ax.legend(legend_handles, [f"{label} ({notation})" for label, notation in
                                            zip(legend_labels, legend_notations)],
                            loc='upper right', bbox_to_anchor=(0.69, 0), facecolor = '#162858', labelcolor='#8ae4ff')

        # Add the legend to the subplot
        ax.add_artist(legend)
        ax.set_facecolor("#11224e")

    plt.subplots_adjust(wspace=0.8)  # Adjust the spacing between subplots
    html_string = mpld3.fig_to_html(fig)
    # plt.savefig('static/temp_file5.png')  # Save the plot as a static file
    # Create a buffer to store the plot image
    # buffer = io.BytesIO()

    # # Save the plot to the buffer
    # plt.savefig(buffer, format='png')
    # buffer.seek(0)

    # # Convert the plot image to a base64-encoded string
    # pie_data = base64.b64encode(buffer.getvalue()).decode('utf-8')

# Generate the HTML code to embed the plot



    # _________________________________________________________________________________________

    query = "SELECT * FROM gps_data ORDER BY id DESC LIMIT 50 "
    data = pd.read_sql(query, connection)

    plot_data = generate_plot(data)

    connection.close()

    num_values = int(request.args.get('num_values', 10))
    last_values = data.tail(num_values)

    quality_1_mean = round(mean(last_values['quality_1']), 2)
    quality_1_median = round(median(last_values['quality_1']), 2)
    quality_1_mode = round(mode(last_values['quality_1']), 2)
    temperature_mean = round(mean(last_values['temperature']), 2)
    temperature_median = round(median(last_values['temperature']), 2)
    temperature_mode = round(mode(last_values['temperature']), 2)
    quality_2_mean = round(mean(last_values['quality_2']), 2)
    quality_2_median = round(median(last_values['quality_2']), 2)
    quality_2_mode = round(mode(last_values['quality_2']), 2)
    quality_3_mean = round(mean(last_values['quality_3']), 2)
    quality_3_median = round(median(last_values['quality_3']), 2)
    quality_3_mode = round(mode(last_values['quality_3']), 2)

    return render_template('indexgr.html', plot_data=plot_data, quality_2_mode=quality_2_mode, quality_2_median=quality_2_median, quality_2_mean=quality_2_mean,
                           temperature_mean=temperature_mean, temperature_median=temperature_median,
                           temperature_mode=temperature_mode, quality_1_mode=quality_1_mode, quality_1_median=quality_1_median, quality_1_mean=quality_1_mean,
                           quality_3_mode=quality_3_mode, quality_3_median=quality_3_median, quality_3_mean=quality_3_mean,
                           bargraph_data=bargraph_data, html_string=html_string)


if __name__ == '__main__':
    subscriber_process = multiprocessing.Process(target=run_subscriber)
    subscriber_process.start()
    app.run()
    subscriber_process.join()
