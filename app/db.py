import os 
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


cluster = MongoClient(os.environ['MONGO_URL'])
db = cluster[os.environ['DB_NAME']]
game_collection = db['GameSave']
user_collection = db['User']

try:
    cluster.admin.command('ping')
    print('INFO:', '\t', 'connected to database')
except ConnectionFailure:
    print("Server not available")
except Exception:
    print("Unable to connect database")