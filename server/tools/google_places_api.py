import os
import requests
import uuid
from typing import List, Dict, Optional, Union

class GooglePlacesAPI:
    def __init__(self, api_key: Optional[str] = None):
        """Google Places API 클라이언트 초기화"""
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise RuntimeError("GOOGLE_API_KEY 미설정")
        
        self.base_headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key
        }
        
    def _create_session_token(self) -> str:
        """새로운 세션 토큰 생성"""
        return str(uuid.uuid4())
    
    def _get_headers(self, field_mask: str) -> Dict[str, str]:
        """API 요청에 사용할 헤더 생성"""
        headers = self.base_headers.copy()
        headers["X-Goog-FieldMask"] = field_mask
        return headers
    
    def search_text(self, 
                   text_query: str, 
                   page_size: int = 10,
                   location_bias: Optional[Dict] = None,
                   session_token: Optional[str] = None) -> List[Dict]:
        """텍스트 기반 장소 검색"""
        url = "https://places.googleapis.com/v1/places:searchText"
        body = {
            "textQuery": text_query,
            "pageSize": page_size
        }
        
        if location_bias:
            body["locationBias"] = location_bias
            
        if session_token:
            body["sessionToken"] = session_token
            
        headers = self._get_headers("places.displayName,places.formattedAddress,places.id,places.types")
        r = requests.post(url, json=body, headers=headers)
        r.raise_for_status()
        return r.json().get("places", [])
    
    def get_place_details(self, 
                         place_id: str,
                         field_mask: str = "displayName,formattedAddress,rating,reviews,generativeSummary,reviewSummary,neighborhoodSummary") -> Dict:
        """장소 상세 정보 조회"""
        url = f"https://places.googleapis.com/v1/places/{place_id}"
        headers = self._get_headers(field_mask)
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        return r.json()
    
    def search_nearby(self,
                     latitude: float,
                     longitude: float,
                     radius: float = 1000,
                     types: Optional[List[str]] = None,
                     page_size: int = 10) -> List[Dict]:
        """주변 장소 검색"""
        url = "https://places.googleapis.com/v1/places:searchNearby"
        body = {
            "locationRestriction": {
                "circle": {
                    "center": {
                        "latitude": latitude,
                        "longitude": longitude
                    },
                    "radius": radius
                }
            },
            "maxResultCount": page_size
        }
        
        if types:
            body["includedTypes"] = types
            
        headers = self._get_headers("places.displayName,places.formattedAddress,places.id,places.types,places.generativeSummary,places.reviewSummary")
        r = requests.post(url, json=body, headers=headers)
        r.raise_for_status()
        return r.json().get("places", [])
    
    def get_place_reviews(self, place_id: str) -> Dict:
        """장소 리뷰 정보 조회"""
        return self.get_place_details(place_id, "reviews,rating,userRatingCount")
    
    def get_place_summary(self, place_id: str) -> Dict:
        """장소 요약 정보 조회 (AI 기반)"""
        return self.get_place_details(place_id, "generativeSummary,reviewSummary")
    
    def get_neighborhood_summary(self, place_id: str) -> Dict:
        """주변 지역 요약 정보 조회 (AI 기반)"""
        return self.get_place_details(place_id, "neighborhoodSummary")
    
    def get_ev_charging_summary(self, place_id: str) -> Dict:
        """전기차 충전소 주변 편의시설 요약 조회"""
        return self.get_place_details(place_id, "evChargeAmenitySummary")

if __name__ == "__main__":
    # 사용 예시
    try:
        api = GooglePlacesAPI()
        
        # 텍스트 검색 예시
        places = api.search_text("카페 서울", page_size=5)
        print("=== 검색 결과 ===")
        for place in places:
            name = place.get("displayName", {}).get("text")
            address = place.get("formattedAddress")
            print(f"{name} - {address}")
            
        # 장소 상세 정보 조회 예시
        if places:
            place_id = places[0].get("id")
            details = api.get_place_details(place_id)
            print("\n=== 장소 상세 정보 ===")
            print(f"이름: {details.get('displayName', {}).get('text')}")
            print(f"주소: {details.get('formattedAddress')}")
            
            # AI 기반 요약 정보
            if "generativeSummary" in details:
                print("\n=== AI 요약 ===")
                print(details["generativeSummary"].get("overview", {}).get("text"))
                
    except Exception as e:
        print("Error:", e)