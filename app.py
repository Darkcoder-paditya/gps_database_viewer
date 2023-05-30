from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient

app = Flask(__name__)

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
def display_data():
    data = collection.find()
    return render_template('./index.html', data=data)

if __name__ == '__main__':
    app.run()