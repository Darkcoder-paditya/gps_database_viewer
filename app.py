
    
    # app.py
import multiprocessing, subprocess
from flask import Flask, render_template, jsonify
from pymongo import MongoClient

app = Flask(__name__, static_folder='static')

# MongoDB configuration
MONGO_HOST = 'mongodb+srv://pa:prashant@cluster0.5b0djvj.mongodb.net/'
MONGO_PORT = 27017
MONGO_DB = 'gps_data'
COLLECTION_NAME = 'gps_messages'
USERNAME = 'pa'
PASSWORD = 'prashant'

# Connect to MongoDB
mongo_client = MongoClient(MONGO_HOST, MONGO_PORT, username=USERNAME, password=PASSWORD)
db = mongo_client[MONGO_DB]
collection = db[COLLECTION_NAME]

@app.route('/delete', methods=['DELETE'])
def delete_data():
    try:
        result = collection.delete_many({})
        deleted_count = result.deleted_count
        return jsonify({'message': 'Data deleted successfully', 'deleted_count': deleted_count}), 200
    except Exception as e:
        return jsonify({'message': 'Failed to delete data', 'error': str(e)}), 500



@app.route('/')
@app.route('/<robot_ids>')
def display_data_route(robot_ids=None):
    if robot_ids:
        robot_id_list = robot_ids.split(',')
        data = collection.find({'robid': {'$in': robot_id_list}})
    else:
        data = collection.find()
    
    return render_template('./index.html', data=data)


def run_subscriber():
    subprocess.run(['python', './subscribe.py'])

if __name__ == '__main__':
    subscriber_process = multiprocessing.Process(target=run_subscriber)
    subscriber_process.start()
    app.run()
    
    subscriber_process.join()
    