import os
import requests

# 1) Naver Cloud Platform에서 발급받은 키
CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
if not CLIENT_ID or not CLIENT_SECRET:
    raise RuntimeError("NAVER_CLIENT_ID/SECRET 환경변수를 설정하세요.")

def naver_local_search(query: str, display: int = 5, start: int = 1):
    """
    키워드로 장소 검색을 수행합니다.
    - query: 검색어
    - display: 한 번에 받아올 결과 수
    - start: 시작 위치(1부터)
    """
    url = "https://naveropenapi.apigw.ntruss.com/map-place/v1/search"
    headers = {
        "X-NCP-APIGW-API-KEY-ID": CLIENT_ID,
        "X-NCP-APIGW-API-KEY": CLIENT_SECRET
    }
    params = {"query": query, "display": display, "start": start}
    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()
    return resp.json().get("places", [])


if __name__ == "__main__":
    places = naver_local_search("카페", display=5)
    print("=== 네이버 장소 검색 ===")
    for p in places:
        print(p["place_name"], "-", p["road_address_name"])