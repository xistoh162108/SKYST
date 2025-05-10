# server/llm/people_photo.py
from typing import List, Dict, Optional
from bson import ObjectId

class PeoplePhotoService:
    def __init__(self, photo_people_repo):
        self.photo_people_repo = photo_people_repo
    
    def get_photos_by_person(self, person_id: str) -> List[Dict]:
        """특정 사람이 포함된 모든 사진을 가져옵니다."""
        query = {"personId": ObjectId(person_id)}
        return self.photo_people_repo.get_photoPeople(query)
    
    def get_people_in_photo(self, photo_id: str) -> List[Dict]:
        """특정 사진에 포함된 모든 사람을 가져옵니다."""
        query = {"photoId": ObjectId(photo_id)}
        return self.photo_people_repo.get_photoPeople(query)
    
    def add_person_to_photo(self, photo_id: str, person_id: str) -> Dict:
        """사진에 사람을 추가합니다."""
        data = {
            "photoId": ObjectId(photo_id),
            "personId": ObjectId(person_id)
        }
        return self.photo_people_repo.add_photoPeople(data)