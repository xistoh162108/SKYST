from db.people import PeopleRepository
from bson import ObjectId
from typing import Optional, Dict, List

def get_person_by_id(repo: PeopleRepository, person_id: str) -> Optional[Dict]:
    """ID로 사람을 검색합니다."""
    query = {"_id": ObjectId(person_id)}
    result = repo.get_person(query)
    return result[0] if result else None

def get_all_people(repo: PeopleRepository) -> List[Dict]:
    """모든 사람 정보를 가져옵니다."""
    return repo.get_person({})