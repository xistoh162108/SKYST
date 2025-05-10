from .db import MongoDBClient

class TravelRepository:
    def __init__(self, db_name: str = "skyst"):
        self.client = MongoDBClient(db_name=db_name)
        self.collection_name = "travels"

    def add_travel(self, data: dict):
        return self.client.create(self.collection_name, data)

    def get_travel(self, query: dict):
        return self.client.read(self.collection_name, query)

    def update_travel(self, query: dict, update_data: dict):
        return self.client.update(self.collection_name, query, update_data)

    def delete_travel(self, query: dict):
        return self.client.delete(self.collection_name, query)
