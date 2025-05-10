from typing import Dict, Any, Optional, List
from .google_places_api import GooglePlacesAPI
from .google_search_api import GoogleSearchAPI
from .tool_list import TOOL_LIST
from tools.people_photo import (
    get_photos_by_person,
    get_people_in_photo,
    add_person_to_photo,
)
from tools.people import get_person_by_id, get_all_people
from tools.photos import search_photo_by_id

class Tools:
    def __init__(self, photo_people_repo, photo_repo, people_repo):
        self.google_places_api = GooglePlacesAPI()
        self.google_search_api = GoogleSearchAPI()
        self.photo_people_repo = photo_people_repo
        self.photo_repo = photo_repo
        self.people_repo = people_repo

        self.tool_mapping = {
            "1": lambda person_id: get_photos_by_person(self.photo_people_repo, person_id),
            "2": lambda photo_id: get_people_in_photo(self.photo_people_repo, photo_id),
            "3": lambda photo_id, person_id: add_person_to_photo(self.photo_people_repo, photo_id, person_id),
            # "4": plan_route
            "5": self.google_places_api.search_text,
            "6": self.google_places_api.get_place_details,
            "7": self.google_places_api.search_nearby,
            "9": self.google_search_api.search,
            "10": self.google_search_api.get_total_results,
            "11": self.google_search_api.get_page_content,
            "16": lambda person_id: get_person_by_id(self.people_repo, person_id),
            "17": lambda: get_all_people(self.people_repo),
        }

    def get_tool_info(self, tool_id: str) -> Optional[Dict[str, Any]]:
        return TOOL_LIST.get(tool_id)

    def execute_tool(self, tool_id: str, **kwargs) -> Any:
        if tool_id not in self.tool_mapping:
            raise ValueError(f"Unknown tool ID: {tool_id}")
        
        tool_info = self.get_tool_info(tool_id)
        if not tool_info:
            raise ValueError(f"No information found for tool ID: {tool_id}")
        
        required_inputs = {
            k: v for k, v in tool_info["inputs"].items() 
            if "Optional" not in v
        }
        missing_inputs = [k for k in required_inputs if k not in kwargs]
        if missing_inputs:
            raise ValueError(f"Missing required inputs for tool {tool_id}: {missing_inputs}")
        
        return self.tool_mapping[tool_id](**kwargs)
    
    def get_tool_list(self) -> Dict[str, Any]:
        return TOOL_LIST