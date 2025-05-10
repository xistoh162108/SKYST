from typing import Dict, Any, Optional, List
from .google_places_api import GooglePlacesAPI
from .google_search_api import GoogleSearchAPI
from .photos import PhotoSearchRepository
from .people_photo import PeoplePhotoService
from .people import PeopleService
from .tool_list import TOOL_LIST

class Tools:
    def __init__(self, photo_people_repo, photo_repo, people_repo):
        # 각 도구 클래스 초기화
        self.google_places_api = GooglePlacesAPI()
        self.google_search_api = GoogleSearchAPI()
        self.photo_search = photo_repo
        self.people_photo = photo_people_repo
        self.people = people_repo
        # 도구 ID와 실제 호출 가능한 함수 매핑
        self.tool_mapping = {
            "1": self.people_photo.get_photos_by_person,
            "2": self.people_photo.get_people_in_photo,
            "3": self.people_photo.add_person_to_photo,
            # "4": plan_route (미구현이므로 주석 처리하거나 구현 후 추가)
            "5": self.google_places_api.search_text,
            "6": self.google_places_api.get_place_details,
            "7": self.google_places_api.search_nearby,
            "9": self.google_search_api.search,
            "10": self.google_search_api.get_total_results,
            "11": self.google_search_api.get_page_content,
            "12": self.google_search_api.download_site,
            # 추가 툴 ID(13,14,...)는 TOOL_LIST에 정의된 후 이어서 매핑
        }
    
    def get_tool_info(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """도구 ID에 대한 정보를 반환합니다."""
        return TOOL_LIST.get(tool_id)
    
    def execute_tool(self, tool_id: str, **kwargs) -> Any:
        """도구 ID와 필요한 파라미터를 받아 도구를 실행합니다."""
        if tool_id not in self.tool_mapping:
            raise ValueError(f"Unknown tool ID: {tool_id}")
        
        tool_info = self.get_tool_info(tool_id)
        if not tool_info:
            raise ValueError(f"No information found for tool ID: {tool_id}")
        
        # 필수 입력 파라미터 확인
        required_inputs = {
            k: v for k, v in tool_info["inputs"].items() 
            if "Optional" not in v
        }
        
        missing_inputs = [
            k for k in required_inputs.keys() 
            if k not in kwargs
        ]
        
        if missing_inputs:
            raise ValueError(
                f"Missing required inputs for tool {tool_id}: {missing_inputs}"
            )
        
        # 도구 실행
        return self.tool_mapping[tool_id](**kwargs)

# 사용 예시
if __name__ == "__main__":
    tools = Tools()
    
    # 도구 정보 조회
    tool_info = tools.get_tool_info("13")  # photo_search_by_id
    print("=== 도구 정보 ===")
    print(f"이름: {tool_info['name']}")
    print(f"설명: {tool_info['description']}")
    print(f"필수 입력: {tool_info['inputs']}")
    print(f"출력: {tool_info['outputs']}")
    
    # 도구 실행 예시
    try:
        # 사진 ID로 검색
        result = tools.execute_tool(
            "13",  # photo_search_by_id
            photo_id="65f1234567890abcdef12345"
        )
        print("\n=== 검색 결과 ===")
        print(result)
        
        # 태그로 사진 검색
        result = tools.execute_tool(
            "2",  # photo_tag_search
            tags=["여행", "바다"],
            limit=5
        )
        print("\n=== 태그 검색 결과 ===")
        print(result)
        
    except ValueError as e:
        print(f"에러: {e}")