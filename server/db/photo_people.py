from .db import MongoDBClient
from server.tools.people_photo import PeoplePhoto

class PhotoPeopleRepository:
    def __init__(self, db_name: str = "skyst"):
        self.client = MongoDBClient(db_name=db_name)
        self.collection_name = "photo_people"
        self.service = PeoplePhotoService()

    def add_photoPeople(self, data: dict):
        return self.client.create(self.collection_name, data)

    def get_photoPeople(self, query: dict):
        return self.client.read(self.collection_name, query)

    def update_photoPeople(self, query: dict, update_data: dict):
        return self.client.update(self.collection_name, query, update_data)

    def delete_photoPeople(self, query: dict):
        return self.client.delete(self.collection_name, query)
    