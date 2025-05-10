

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
        "name": "get_photos_by_person",
        "module": "tools.people_photo",
        "callable": "get_photos_by_person",
        "description": "사람 ObjectId(또는 이름)를 받아 해당 인물이 포함된 모든 사진을 반환합니다.",
        "inputs": {
            "person_id": "str — 필수. 인물의 BSON ObjectId 또는 이름"
        },
        "outputs": {
            "photos": "List[Dict] — 사진 메타데이터 목록",
            "count": "int — 검색된 사진 수"
        },
    },
    "2": {
        "name": "get_people_in_photo",
        "module": "tools.people_photo",
        "callable": "get_people_in_photo",
        "description": "사진 ID를 받아 해당 사진에 등장하는 모든 사람(인물) 정보를 반환합니다.",
        "inputs": {
            "photo_id": "str — 필수. BSON ObjectId 형식의 사진 ID"
        },
        "outputs": {
            "people": "List[Dict] — 인물 메타데이터 목록",
            "count": "int — 검색된 인물 수"
        },
    },
    "3": {
        "name": "add_person_to_photo",
        "module": "tools.people_photo",
        "callable": "add_person_to_photo",
        "description": "사진‑인물 매핑을 추가하여 특정 사진에 사람을 연결합니다.",
        "inputs": {
            "photo_id": "str — 필수. BSON ObjectId 형식의 사진 ID",
            "person_id": "str — 필수. BSON ObjectId 형식의 인물 ID"
        },
        "outputs": {
            "mapping": "Dict — 저장된 매핑 문서"
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
     "16": {
        "name": "get_person_by_id",
        "module": "tools.people",
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
        "module": "tools.people",
        "callable": "get_all_people",
        "description": "모든 인물 정보 목록을 반환합니다.",
        "inputs": {},  # 입력 파라미터 없음
        "outputs": {
            "people": "List[Dict] — 인물 메타데이터 목록"
        },
    },
    "18": {
        "name": "search_photo_by_id",
        "module": "tools.photos",
        "callable": "search_photo_by_id",
        "description": "사진 ID를 받아 해당 사진의 메타데이터를 반환합니다.",
        "inputs": {
            "photo_id": "str — 필수. BSON ObjectId 형식의 사진 ID"
        },
        "outputs": {
            "photo": "Dict — 사진 메타데이터 (없으면 null)"
        },
    },
    # -------------------------------------------------------------
    # 추가된 LLM 기반 툴 정의 (ID 19‒23)
    # -------------------------------------------------------------------
    "19": {
        "name": "input_checker",
        "module": "llm.models",
        "callable": "inputChecker.process_query",
        "description": "사용자 입력이 여행·장소 추천 도메인에 맞는지 판단합니다.",
        "inputs": {
            "user_message": "str — 필수. 사용자 메시지"
        },
        "outputs": {
            "is_valid": "bool — 입력 적합 여부 (true/false)"
        },
    },
    "20": {
        "name": "query_maker",
        "module": "llm.models",
        "callable": "queryMaker.process_query",
        "description": "사용자 요청을 다양한 측면에서 검색할 수 있는 쿼리 목록을 생성합니다.",
        "inputs": {
            "user_message": "str — 필수. 사용자 메시지"
        },
        "outputs": {
            "queries": "List[str] — 생성된 검색 쿼리 목록"
        },
    },
    "21": {
        "name": "filter_generator",
        "module": "llm.models",
        "callable": "filterGenerator.process_query",
        "description": "사용자 메시지에서 핵심 키워드(최대 3개)를 추출합니다.",
        "inputs": {
            "user_message": "str — 필수. 사용자 메시지"
        },
        "outputs": {
            "filter_words": "List[str] — 추출된 필터 단어"
        },
    },
    "22": {
        "name": "tot_maker",
        "module": "llm.models",
        "callable": "TOTMaker.process_query",
        "description": "사용 가능한 도구를 활용하여 Tree‑of‑Thoughts 실행 계획을 생성합니다.",
        "inputs": {
            "user_message": "str — 필수. 사용자 메시지"
        },
        "outputs": {
            "steps": "List[Dict] — 단계별 도구 사용 계획"
        },
    },
    "23": {
        "name": "tot_executor",
        "module": "llm.models",
        "callable": "TOTExecutor.execute_plan",
        "description": "Tree‑of‑Thoughts 실행 계획을 단계별로 실행하고 결과를 반환합니다.",
        "inputs": {
            "plan": "Dict — 필수. TOTMaker가 생성한 실행 계획"
        },
        "outputs": {
            "steps": "List[Dict] — 단계별 실행 결과",
            "final_summary": "str — 전체 실행 결과 요약"
        },
    },
    "24": {
        "name": "summarize_text",
        "description": "주어진 텍스트를 요약합니다.",
        "inputs": {
            "text": "str — 요약할 텍스트"
        },
        "outputs": {
            "summary": "str — 텍스트의 요약",
            "key_points": "List[str] — 핵심 포인트 목록",
            "length_ratio": "float — 요약 길이 / 원문 길이 비율"
        }
    },
    "25": {
        "name": "generate_response",
        "description": "커스텀 LLM을 사용하여 프롬프트에 대한 응답을 생성합니다.",
        "inputs": {
            "prompt": "str — 사용자 프롬프트",
            "system_prompt": "Optional[str] — 시스템 프롬프트",
            "temperature": "Optional[float] — 생성 온도 (0.0 ~ 1.0)"
        },
        "outputs": {
            "response": "str — 생성된 응답"
        }
    },
    "26": {
        "name": "generate_with_context",
        "description": "컨텍스트가 포함된 프롬프트에 대한 응답을 생성합니다.",
        "inputs": {
            "prompt": "str — 사용자 프롬프트",
            "context": "str — 컨텍스트 정보",
            "system_prompt": "Optional[str] — 시스템 프롬프트",
            "temperature": "Optional[float] — 생성 온도 (0.0 ~ 1.0)"
        },
        "outputs": {
            "response": "str — 생성된 응답"
        }
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