import pandas as pd
import datetime
import matplotlib.pyplot as plt
from matplotlib import style
style.use('ggplot')

# # read data and create a df, it will take all page tables

import mysql.connector

try:
    connection = mysql.connector.connect(host='localhost',
                                         database='gps_data',
                                         user='root',
                                         password='root')
    sql_query = pd.read_sql('SELECT * FROM gps_data', connection)
    print(connection)
    df = pd.DataFrame(sql_query, columns = [ 'id', 'robot_id','temperature', 'latitude', 'longitude'])
    
    # sql_select_Query = "select * from gps_data"
    # cursor = connection.cursor()
    # cursor.execute(sql_select_Query)
    # get all records
    
    # df = pd.read_sql_table
    # df = df[0]
    # df.set_index(df.columns[0],).plot(figsize=(15,8))
    # print(df)
    

# Save the plots as PNG images
    df.plot(df.columns[0], df.columns[2], figsize=(18, 8))
    plt.savefig('./webpage/temperature.png')

    df.plot(df.columns[0], df.columns[3], figsize=(18, 8))
    plt.savefig('./webpage/latitude.png')

    df.plot(df.columns[0], df.columns[4], figsize=(18, 8))
    plt.savefig('./webpage/longitude.png')

    # Close the plots
    plt.close('all')
    # plt.show()
    

except mysql.connector.Error as e:
    print("Error reading data from MySQL table", e)