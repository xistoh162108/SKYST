from db.people import PeopleRepository
from bson import ObjectId
from typing import Optional, Dict, List

class PeopleService:
    def __init__(self, db_name: str = "skyst"):
        self.people_repo = PeopleRepository(db_name)
    
    def get_person_by_id(self, person_id: str) -> Optional[Dict]:
        """ID로 사람을 검색합니다."""
        query = {"_id": ObjectId(person_id)}
        result = self.people_repo.get_person(query)
        return result[0] if result else None
    
    def get_all_people(self) -> List[Dict]:
        """모든 사람 정보를 가져옵니다."""
        return self.people_repo.get_person({})