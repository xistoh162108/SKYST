# server/db/photo_search.py
from db.photos import PhotoRepository
from bson import ObjectId
from typing import Optional, Dict

class PhotoSearchRepository(PhotoRepository):
    def __init__(self, db_name: str = "skyst"):
        super().__init__(db_name)
    
    def search_by_id(self, photo_id: str) -> Optional[Dict]:
        """ID로 사진을 검색합니다."""
        query = {"_id": ObjectId(photo_id)}
        result = self.get_photo(query)
        return result[0] if result else None