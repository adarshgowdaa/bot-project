from pymongo import MongoClient
import redis
from dotenv import load_dotenv
import os

load_dotenv()

mongo_uri = os.getenv('MONGO_URI')
db_name = os.getenv('MONGO_DB_NAME')

client = MongoClient(mongo_uri)
db = client[db_name]
users_collection = db['users']
chat_collection = db['chat']

redis_host = os.getenv('REDIS_HOST')
redis_port = os.getenv('REDIS_PORT')
redis_db = os.getenv('REDIS_DB')

r = redis.StrictRedis(host=redis_host, port=redis_port, db=int(redis_db), decode_responses=True)
