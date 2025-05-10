from .db import MongoDBClient


class PhotoRepository:
    def __init__(self, db_name: str = "skyst"):
        self.client = MongoDBClient(db_name=db_name)
        self.collection_name = "photos"

    def add_photo(self, data: dict):
        return self.client.create(self.collection_name, data)

    def get_photo(self, query: dict):
        return self.client.read(self.collection_name, query)

    def update_photo(self, query: dict, update_data: dict):
        return self.client.update(self.collection_name, query, update_data)

    def delete_photo(self, query: dict):
        return self.client.delete(self.collection_name, query)