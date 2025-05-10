# people.py
from .db import MongoDBClient

def add_person(data):
    client = MongoDBClient(db_name="skyst")
    collection = client["people"]
    return collection.insert_one(data)

def get_person(data):
    client = MongoDBClient(db_name="skyst")
    collection = client["people"]
    return collection.find_one(data)

def update_person(data):
    client = MongoDBClient(db_name="skyst")
    collection = client["people"]
    return collection.update_one(data)

def delete_person(data):
    client = MongoDBClient(db_name="skyst")
    collection = client["people"]
    return collection.delete_one(data)