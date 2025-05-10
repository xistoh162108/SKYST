# examples/google_places_demo.py

from tools.google_places_api import GooglePlacesAPI
from tools.google_search_api import GoogleSearchAPI
from server.llm.models import GeminiLLM

def main():
    api = GooglePlacesAPI()
    
    # 1) 텍스트 검색
    print("=== 1) 텍스트 검색 (search_text) ===")
    places = api.search_text("카페 서울", page_size=3)
    for idx, place in enumerate(places, 1):
        name = place.get("displayName", {}).get("text")
        addr = place.get("formattedAddress")
        pid  = place.get("id")
        print(f"{idx}. {name} | {addr} | place_id={pid}")
    print()

    if not places:
        print("검색 결과가 없습니다. API 설정을 확인하세요.")
        return

    # 가장 첫 장소 ID
    first_id = places[0]["id"]

    # 2) 장소 상세 정보
    print("=== 2) 장소 상세 정보 (get_place_details) ===")
    details = api.get_place_details(first_id)
    print("Name:", details.get("displayName", {}).get("text"))
    print("Address:", details.get("formattedAddress"))
    print("Rating:", details.get("rating"))
    print()

    # 3) 장소 리뷰
    print("=== 3) 장소 리뷰 (get_place_reviews) ===")
    reviews = api.get_place_reviews(first_id)
    print(reviews.get("reviews", []))
    print()

    # 7) 주변 검색 (search_nearby)
    print("=== 7) 주변 검색 (search_nearby) ===")
    # 첫 장소의 좌표가 필요하다면 details 안에 location 필드를 요청하도록 수정하세요.
    # 여기서는 임의 좌표(서울 시청) 사용 예시
    nearby = api.search_nearby(latitude=37.5665, longitude=126.9780, radius=500, types=["restaurant"], page_size=3)
    for idx, place in enumerate(nearby, 1):
        name = place.get("displayName", {}).get("text")
        print(f"{idx}. {name}")
    print()

    # 8) 구글 웹 검색 (GoogleSearchAPI)
    print("=== 8) 구글 웹 검색 (search) ===")
    search_api = GoogleSearchAPI()
    search_results = search_api.search("OpenAI", num=3)
    for idx, item in enumerate(search_results, 1):
        title = item.get("title")
        link = item.get("link")
        snippet = item.get("snippet")
        print(f"{idx}. {title}\n   {link}\n   {snippet}\n")


    # 9) 웹 페이지 콘텐츠 가져오기 (get_page_content)
    print("=== 9) 웹 페이지 콘텐츠 가져오기 ===")
    if search_results:
        sample_url = search_results[0].get("link")
        try:
            content = search_api.get_page_content(sample_url)
            print(content[:500])  # 앞 500자만 출력
        except Exception as e:
            print("페이지 콘텐츠 가져오기 오류:", e)
    print()

    # 10) 사이트 전체 다운로드 (download_site)
    print("=== 10) 사이트 전체 다운로드 ===")
    if search_results:
        sample_url = search_results[0].get("link")
        target_dir = "downloaded_site"
        try:
            search_api.download_site(sample_url, target_dir)
            print(f"사이트가 '{target_dir}' 폴더에 다운로드되었습니다.")
        except Exception as e:
            print("사이트 다운로드 오류:", e)
    print()
 
    # 11) Gemini 멀티모달 테스트 (이미지 입력)
    print("=== 11) Gemini 멀티모달 테스트 (이미지 설명) ===")
    try:
        gemini = GeminiLLM()
        description = gemini.generate_response(
            prompt="이 이미지에 대해 설명해줘.",
            image_path="test_assets/Eastern Bluebird.jpg"
        )
        print(description)
    except Exception as e:
        print("Gemini 이미지 테스트 오류:", e)
    print()

if __name__ == "__main__":
    main()