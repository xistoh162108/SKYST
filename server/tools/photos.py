from db.photos import PhotoRepository
from bson import ObjectId
from typing import Optional, Dict

def search_photo_by_id(repo: PhotoRepository, photo_id: str) -> Optional[Dict]:
    """ID로 사진을 검색합니다."""
    query = {"_id": ObjectId(photo_id)}
    result = repo.get_photo(query)
    return result[0] if result else None