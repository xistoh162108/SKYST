# server/db/people.py
from . import MongoDBClient

class PeopleRepository:
    def __init__(self, db_name: str = "skyst"):
        self.client = MongoDBClient(db_name=db_name)
        self.collection_name = "people"

    def add_person(self, data: dict):
        return self.client.create(self.collection_name, data)

    def get_person(self, query: dict):
        return self.client.read(self.collection_name, query)

    def update_person(self, query: dict, update_data: dict):
        return self.client.update(self.collection_name, query, update_data)

    def delete_person(self, query: dict):
        return self.client.delete(self.collection_name, query)