# photos.py
from .db import MongoDBClient

def add_photo(data):
    client = MongoDBClient(db_name="skyst")
    collection = client["photos"]
    return collection.insert_one(data)

def get_photo(data):
    client = MongoDBClient(db_name="skyst")
    collection = client["photos"]
    return collection.find_one(data)

def update_photo(data):
    client = MongoDBClient(db_name="skyst")
    collection = client["photos"]
    return collection.update_one(data)

def delete_photo(data):
    client = MongoDBClient(db_name="skyst")
    collection = client["photos"]
    return collection.delete_one(data)