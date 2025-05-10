# tools/people_photo.py
from bson import ObjectId

def get_photos_by_person(photo_people_repo, person_id: str):
    return photo_people_repo.get_photoPeople({"personId": ObjectId(person_id)})

def get_people_in_photo(photo_people_repo, photo_id: str):
    return photo_people_repo.get_photoPeople({"photoId": ObjectId(photo_id)})

def add_person_to_photo(photo_people_repo, photo_id: str, person_id: str):
    return photo_people_repo.add_photoPeople({
        "photoId": ObjectId(photo_id),
        "personId": ObjectId(person_id)
    })