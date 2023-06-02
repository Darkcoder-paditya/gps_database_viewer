
# Generate random values and insert into the table
for _ in range(2):  # Generate 2 random records
    serial_number = random.randint(1, 100)
    data_id = 'data_' + str(random.randint(1, 100))
    robot_id = 'robot_' + str(random.randint(1, 100))
    topic = 'topic_' + str(random.randint(1, 100))
    temperature = round(random.uniform(-20, 50), 2)
    latitude = round(random.uniform(-90, 90), 6)
    longitude = round(random.uniform(-180, 180), 6)

    insert_query = "INSERT INTO gps_data (serial_number, data_id, robot_id, topic, temperature, latitude, longitude) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    insert_values = (serial_number, data_id, robot_id, topic, temperature, latitude, longitude)
    mysql_cursor.execute(insert_query, insert_values)

mysql_connection.commit()
mysql_cursor.close()
mysql_connection.close()
