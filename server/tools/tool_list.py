

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
    }
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