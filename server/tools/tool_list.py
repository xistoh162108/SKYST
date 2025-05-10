

"""
Central registry of planning‑agent tools.

Each tool is referenced by a **string ID** (e.g. "1") and described with
metadata that can be consumed by other components (e.g. totMaker).

No runtime bindings are performed here; only static metadata is provided.
Actual callable objects are imported and used by the execution engine.
"""

from typing import Dict, Any


# ---------------------------------------------------------------------------
# Tool registry
# ---------------------------------------------------------------------------

TOOL_LIST: Dict[str, Dict[str, Any]] = {
    "1": {
        "name": "people_photo_search",
        "module": "tools.people_photo",
        "callable": "search_by_person",
        "description": "사람 ID(또는 이름)를 받아 photo_people DB에서 해당 인물이 등장하는 사진 목록을 반환합니다.",
        "inputs": {
            "person_id": "str — 필수. 인물의 고유 ID 또는 이름"
        },
        "outputs": {
            "photos": "List[Dict] — 사진 메타데이터 목록",
            "count": "int — 검색된 사진 수"
        },
    },
    "2": {
        "name": "photo_tag_search",
        "module": "tools.photo",
        "callable": "search_by_tags",
        "description": "태그(키워드) 리스트를 받아 사진 DB에서 일치/유사 태그를 가진 사진을 검색합니다.",
        "inputs": {
            "tags": "List[str] — 필수. 검색할 태그 목록",
            "limit": "Optional[int] — 최대 반환 개수 (기본값 50)"
        },
        "outputs": {
            "photos": "List[Dict] — 사진 메타데이터 목록",
            "count": "int — 검색된 사진 수"
        },
    },
    "3": {
        "name": "place_recommender",
        "module": "tools.recommender",
        "callable": "recommend_places",
        "description": "사진·태그·위치 데이터를 분석하여 음식점·카페·관광지를 추천합니다.",
        "inputs": {
            "city": "str — 필수. 도시/지역명",
            "category": "str — 음식, 카페, 관광 등",
            "seed_places": "Optional[List[str]] — 참고할 장소 ID 목록"
        },
        "outputs": {
            "places": "List[Dict] — 추천 장소 목록(이름, 좌표, 설명 등 포함)"
        },
    },
    "4": {
        "name": "route_planner",
        "module": "tools.route",
        "callable": "plan_route",
        "description": "여러 장소 ID와 사용자의 선호 조건을 받아 최적 동선(여행 코스)을 계산합니다.",
        "inputs": {
            "place_ids": "List[str] — 필수. 방문할 장소 ID 순서 미지정",
            "start_time": "str — 여행 시작 시각 (ISO 8601)",
            "constraints": "Optional[Dict] — 이동 수단, 예산, 시간 등"
        },
        "outputs": {
            "route": "List[Dict] — 방문 순서 및 예상 이동·체류 시간",
            "total_time": "float — 총 소요 시간(시간 단위)"
        },
    },
    "5": {
        "name": "gp_search_text",
        "module": "tools.google_places",
        "callable": "search_text",
        "description": "Google Places API 텍스트 기반 장소 검색을 수행합니다.",
        "inputs": {
            "text_query": "str — 필수. 검색할 키워드",
            "page_size": "Optional[int] — 최대 결과 수 (기본값 10)",
            "location_bias": "Optional[Dict] — 위치 바이어스(좌표/반경 등)",
            "session_token": "Optional[str] — 세션 토큰"
        },
        "outputs": {
            "places": "List[Dict] — 검색된 장소 객체 목록"
        },
    },
    "6": {
        "name": "gp_get_place_details",
        "module": "tools.google_places",
        "callable": "get_place_details",
        "description": "장소 ID에 대한 상세 정보를 조회합니다.",
        "inputs": {
            "place_id": "str — 필수. Google Places place_id",
            "field_mask": "Optional[str] — 반환할 필드 마스크 (콤마 구분)"
        },
        "outputs": {
            "place": "Dict — 장소 상세 정보"
        },
    },
    "7": {
        "name": "gp_search_nearby",
        "module": "tools.google_places",
        "callable": "search_nearby",
        "description": "위도·경도·반경을 기준으로 주변 장소를 검색합니다.",
        "inputs": {
            "latitude": "float — 필수. 위도",
            "longitude": "float — 필수. 경도",
            "radius": "Optional[float] — 검색 반경 미터 (기본값 1000)",
            "types": "Optional[List[str]] — 포함할 place types",
            "page_size": "Optional[int] — 최대 결과 수 (기본값 10)"
        },
        "outputs": {
            "places": "List[Dict] — 검색된 장소 객체 목록"
        },
    },
    "9": {
        "name": "gs_search",
        "module": "tools.google_search",
        "callable": "search",
        "description": "Google Custom Search API를 사용하여 웹 검색을 수행합니다.",
        "inputs": {
            "query": "str — 필수. 검색어 또는 구문",
            "num": "Optional[int] — 반환 결과 수 1‑10 (기본값 10)",
            "start": "Optional[int] — 1부터 시작하는 결과 인덱스 (기본값 1)",
            "safe": "Optional[str] — SafeSearch 설정 (off, medium, high)"
        },
        "outputs": {
            "items": "List[Dict] — 검색 결과 아이템 목록"
        },
    },
    "10": {
        "name": "gs_get_total_results",
        "module": "tools.google_search",
        "callable": "get_total_results",
        "description": "검색어에 대한 전체 추정 결과 개수를 반환합니다.",
        "inputs": {
            "query": "str — 필수. 검색어 또는 구문"
        },
        "outputs": {
            "total_results": "int — 추정 결과 개수"
        },
    },
    "11": {
        "name": "gs_get_page_content",
        "module": "tools.google_search",
        "callable": "get_page_content",
        "description": "URL의 HTML 원본을 가져옵니다.",
        "inputs": {
            "url": "str — 필수. 대상 URL"
        },
        "outputs": {
            "html": "str — 페이지 HTML 소스"
        },
    },
    "12": {
        "name": "gs_download_site",
        "module": "tools.google_search",
        "callable": "download_site",
        "description": "wget을 사용해 사이트를 로컬로 미러합니다.",
        "inputs": {
            "url": "str — 필수. 대상 사이트 URL",
            "target_dir": "str — 필수. 저장할 로컬 디렉터리 경로"
        },
        "outputs": {
            "path": "str — 다운로드된 사이트가 저장된 디렉터리"
        },
    },
    "13": {
        "name": "photo_search_by_id",
        "module": "tools.photo_search",
        "callable": "search_by_id",
        "description": "사진 ID(ObjectId)를 받아 단일 사진 메타데이터를 반환합니다.",
        "inputs": {
            "photo_id": "str — 필수. BSON ObjectId 형식의 사진 ID"
        },
        "outputs": {
            "photo": "Dict — 사진 메타데이터 (없으면 null)"
        },
    },
    "14": {
        "name": "people_in_photo",
        "module": "tools.people_photo",
        "callable": "get_people_in_photo",
        "description": "사진 ID로 해당 사진에 포함된 인물(people) 정보를 조회합니다.",
        "inputs": {
            "photo_id": "str — 필수. BSON ObjectId 형식의 사진 ID"
        },
        "outputs": {
            "people": "List[Dict] — 인물 메타데이터 목록"
        },
    },
    "15": {
        "name": "add_person_to_photo",
        "module": "tools.people_photo",
        "callable": "add_person_to_photo",
        "description": "사진‑인물 매핑을 추가하여 사람을 사진에 연결합니다.",
        "inputs": {
            "photo_id": "str — 필수. BSON ObjectId 형식의 사진 ID",
            "person_id": "str — 필수. BSON ObjectId 형식의 인물 ID"
        },
        "outputs": {
            "mapping": "Dict — 저장된 매핑 문서"
        },
    },
        "16": {
        "name": "get_person_by_id",
        "module": "llm.people",
        "callable": "get_person_by_id",
        "description": "인물 ID를 받아 해당 인물의 정보를 반환합니다.",
        "inputs": {
            "person_id": "str — 필수. BSON ObjectId 형식의 인물 ID"
        },
        "outputs": {
            "person": "Dict — 인물 메타데이터 (없으면 null)"
        },
    },
    
    "17": {
        "name": "get_all_people",
        "module": "llm.people",
        "callable": "get_all_people",
        "description": "모든 인물 정보 목록을 반환합니다.",
        "inputs": {},  # 입력 파라미터 없음
        "outputs": {
            "people": "List[Dict] — 인물 메타데이터 목록"
        },
    },
}


# ---------------------------------------------------------------------------
# Helper accessors
# ---------------------------------------------------------------------------

def get_tool_list() -> Dict[str, Dict[str, Any]]:
    """Return a shallow copy of the full tool registry."""
    return TOOL_LIST.copy()


def get_tool_by_id(tool_id: str) -> Dict[str, Any]:
    """Return metadata for a single tool ID, or None if not found."""
    return TOOL_LIST.get(tool_id)