<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> e0c7e6b (middle update)
# server/test.py
from tools.tools import Tools
from db.people import PeopleRepository
from db.photos import PhotoRepository
<<<<<<< HEAD
from db.photo_people import PhotoPeopleRepository
from bson import ObjectId

def create_test_data(photo_repo, people_repo, photo_people_repo):
    """테스트용 더미 데이터를 생성합니다."""
    # 테스트용 사람 데이터 생성
    test_person = {
        "name": "테스트 사용자",
        "email": "test@example.com"
    }
    person_id = people_repo.add_person(test_person)
    print(f"생성된 사람 ID: {person_id}")
    
    # 테스트용 사진 데이터 생성
    test_photo = {
        "image_url": "https://example.com/test.jpg",
        "description": "테스트 사진입니다",
        "tags": ["테스트", "여행", "바다"],
        "location": [37.5665, 126.9780]
    }
    photo_id = photo_repo.add_photo(test_photo)
    print(f"생성된 사진 ID: {photo_id}")
    
    # 사진-사람 매핑 생성
    test_mapping = {
        "photoId": ObjectId(photo_id),
        "personId": ObjectId(person_id)
    }
    mapping_id = photo_people_repo.add_photoPeople(test_mapping)
    print(f"생성된 매핑 ID: {mapping_id}")
    
    return {
        "person_id": str(person_id),
        "photo_id": str(photo_id),
        "mapping_id": str(mapping_id)
    }

def test_all_tools():
     # DB 레포지토리 초기화
    photo_repo = PhotoRepository()
    people_repo = PeopleRepository()
    photo_people_repo = PhotoPeopleRepository()
    print("=== 테스트 데이터 생성 ===")
    test_ids = create_test_data(photo_repo, people_repo, photo_people_repo)
    print(f"생성된 테스트 ID들: {test_ids}\n")
    
    # Tools 인스턴스 생성 시 레포지토리 전달
    tools = Tools(
        photo_repo=photo_repo,
        people_repo=people_repo,
        photo_people_repo=photo_people_repo
    )
    
    print("=== 모든 도구 테스트 시작 ===\n")
    
    # 1. people_photo_search 테스트
    print("1. people_photo_search 테스트")
    try:
        result = tools.execute_tool(
            "1",
            person_id="65f1234567890abcdef12345"  # 더미 person_id
        )
        print(f"결과: {result}\n")
    except Exception as e:
        print(f"에러: {e}\n")
    
    # 2. photo_tag_search 테스트
    print("2. photo_tag_search 테스트")
    try:
        result = tools.execute_tool(
            "2",
            tags=["여행", "바다"],
            limit=5
        )
        print(f"결과: {result}\n")
    except Exception as e:
        print(f"에러: {e}\n")
    
    # 5. gp_search_text 테스트
    print("5. gp_search_text 테스트")
    try:
        result = tools.execute_tool(
            "5",
            text_query="서울 카페",
            page_size=3
        )
        print(f"결과: {result}\n")
    except Exception as e:
        print(f"에러: {e}\n")
    
    # 6. gp_get_place_details 테스트
    print("6. gp_get_place_details 테스트")
    try:
        result = tools.execute_tool(
            "6",
            place_id="ChIJN1t_tDeuEmsRUsoyG83frY4"  # 더미 place_id
        )
        print(f"결과: {result}\n")
    except Exception as e:
        print(f"에러: {e}\n")
    
    # 7. gp_search_nearby 테스트
    print("7. gp_search_nearby 테스트")
    try:
        result = tools.execute_tool(
            "7",
            latitude=37.5665,
            longitude=126.9780,
            radius=1000,
            types=["cafe", "restaurant"]
        )
        print(f"결과: {result}\n")
    except Exception as e:
        print(f"에러: {e}\n")
    
    # 9. gs_search 테스트
    print("9. gs_search 테스트")
    try:
        result = tools.execute_tool(
            "9",
            query="서울 여행 명소",
            num=3
        )
        print(f"결과: {result}\n")
    except Exception as e:
        print(f"에러: {e}\n")
    
    # 10. gs_get_total_results 테스트
    print("10. gs_get_total_results 테스트")
    try:
        result = tools.execute_tool(
            "10",
            query="서울 여행"
        )
        print(f"결과: {result}\n")
    except Exception as e:
        print(f"에러: {e}\n")
    
    # 11. gs_get_page_content 테스트
    print("11. gs_get_page_content 테스트")
    try:
        result = tools.execute_tool(
            "11",
            url="https://www.google.com"
        )
        print(f"결과: {result[:200]}...\n")  # 처음 200자만 출력
    except Exception as e:
        print(f"에러: {e}\n")
    
    # 12. gs_download_site 테스트
    print("12. gs_download_site 테스트")
    try:
        result = tools.execute_tool(
            "12",
            url="https://www.google.com",
            target_dir="./downloaded_sites"
        )
        print(f"결과: {result}\n")
    except Exception as e:
        print(f"에러: {e}\n")
    
    # 13. photo_search_by_id 테스트
    print("13. photo_search_by_id 테스트")
    try:
        result = tools.execute_tool(
            "13",
            photo_id="65f1234567890abcdef12345"  # 더미 photo_id
        )
        print(f"결과: {result}\n")
    except Exception as e:
        print(f"에러: {e}\n")
    
    # 14. people_in_photo 테스트
    print("14. people_in_photo 테스트")
    try:
        result = tools.execute_tool(
            "14",
            photo_id="65f1234567890abcdef12345"  # 더미 photo_id
        )
        print(f"결과: {result}\n")
    except Exception as e:
        print(f"에러: {e}\n")
    
    # 16. get_person_by_id 테스트
    print("16. get_person_by_id 테스트")
    try:
        result = tools.execute_tool(
            "16",
            person_id="65f1234567890abcdef12345"  # 더미 person_id
        )
        print(f"결과: {result}\n")
    except Exception as e:
        print(f"에러: {e}\n")
    
    # 17. get_all_people 테스트
    print("17. get_all_people 테스트")
    try:
        result = tools.execute_tool("17")
        print(f"결과: {result}\n")
    except Exception as e:
        print(f"에러: {e}\n")

if __name__ == "__main__":
    test_all_tools()
=======
=======
>>>>>>> e0c7e6b (middle update)
from db.photo_people import PhotoPeopleRepository
from bson import ObjectId

def create_test_data(photo_repo, people_repo, photo_people_repo):
    """테스트용 더미 데이터를 생성합니다."""
    # 테스트용 사람 데이터 생성
    test_person = {
        "name": "테스트 사용자",
        "email": "test@example.com"
    }
    person_id = people_repo.add_person(test_person)
    print(f"생성된 사람 ID: {person_id}")
    
    # 테스트용 사진 데이터 생성
    test_photo = {
        "image_url": "https://example.com/test.jpg",
        "description": "테스트 사진입니다",
        "tags": ["테스트", "여행", "바다"],
        "location": [37.5665, 126.9780]
    }
    photo_id = photo_repo.add_photo(test_photo)
    print(f"생성된 사진 ID: {photo_id}")
    
    # 사진-사람 매핑 생성
    test_mapping = {
        "photoId": ObjectId(photo_id),
        "personId": ObjectId(person_id)
    }
    mapping_id = photo_people_repo.add_photoPeople(test_mapping)
    print(f"생성된 매핑 ID: {mapping_id}")
    
    return {
        "person_id": str(person_id),
        "photo_id": str(photo_id),
        "mapping_id": str(mapping_id)
    }

def test_all_tools():
     # DB 레포지토리 초기화
    photo_repo = PhotoRepository()
    people_repo = PeopleRepository()
    photo_people_repo = PhotoPeopleRepository()
    print("=== 테스트 데이터 생성 ===")
    test_ids = create_test_data(photo_repo, people_repo, photo_people_repo)
    print(f"생성된 테스트 ID들: {test_ids}\n")
    
    # Tools 인스턴스 생성 시 레포지토리 전달
    tools = Tools(
        photo_repo=photo_repo,
        people_repo=people_repo,
        photo_people_repo=photo_people_repo
    )
    
    print("=== 모든 도구 테스트 시작 ===\n")
    
    # 1. people_photo_search 테스트
    print("1. people_photo_search 테스트")
    try:
        result = tools.execute_tool(
            "1",
            person_id="65f1234567890abcdef12345"  # 더미 person_id
        )
        print(f"결과: {result}\n")
    except Exception as e:
        print(f"에러: {e}\n")
    
    # 2. photo_tag_search 테스트
    print("2. photo_tag_search 테스트")
    try:
        result = tools.execute_tool(
            "2",
            tags=["여행", "바다"],
            limit=5
        )
        print(f"결과: {result}\n")
    except Exception as e:
        print(f"에러: {e}\n")
    
    # 5. gp_search_text 테스트
    print("5. gp_search_text 테스트")
    try:
        result = tools.execute_tool(
            "5",
            text_query="서울 카페",
            page_size=3
        )
        print(f"결과: {result}\n")
    except Exception as e:
        print(f"에러: {e}\n")
    
    # 6. gp_get_place_details 테스트
    print("6. gp_get_place_details 테스트")
    try:
        result = tools.execute_tool(
            "6",
            place_id="ChIJN1t_tDeuEmsRUsoyG83frY4"  # 더미 place_id
        )
        print(f"결과: {result}\n")
    except Exception as e:
        print(f"에러: {e}\n")
    
    # 7. gp_search_nearby 테스트
    print("7. gp_search_nearby 테스트")
    try:
        result = tools.execute_tool(
            "7",
            latitude=37.5665,
            longitude=126.9780,
            radius=1000,
            types=["cafe", "restaurant"]
        )
        print(f"결과: {result}\n")
    except Exception as e:
        print(f"에러: {e}\n")
    
    # 9. gs_search 테스트
    print("9. gs_search 테스트")
    try:
        result = tools.execute_tool(
            "9",
            query="서울 여행 명소",
            num=3
        )
        print(f"결과: {result}\n")
    except Exception as e:
        print(f"에러: {e}\n")
    
    # 10. gs_get_total_results 테스트
    print("10. gs_get_total_results 테스트")
    try:
        result = tools.execute_tool(
            "10",
            query="서울 여행"
        )
        print(f"결과: {result}\n")
    except Exception as e:
        print(f"에러: {e}\n")
    
    # 11. gs_get_page_content 테스트
    print("11. gs_get_page_content 테스트")
    try:
        result = tools.execute_tool(
            "11",
            url="https://www.google.com"
        )
        print(f"결과: {result[:200]}...\n")  # 처음 200자만 출력
    except Exception as e:
        print(f"에러: {e}\n")
    
    # 12. gs_download_site 테스트
    print("12. gs_download_site 테스트")
    try:
        result = tools.execute_tool(
            "12",
            url="https://www.google.com",
            target_dir="./downloaded_sites"
        )
        print(f"결과: {result}\n")
    except Exception as e:
        print(f"에러: {e}\n")
    
    # 13. photo_search_by_id 테스트
    print("13. photo_search_by_id 테스트")
    try:
        result = tools.execute_tool(
            "13",
            photo_id="65f1234567890abcdef12345"  # 더미 photo_id
        )
        print(f"결과: {result}\n")
    except Exception as e:
        print(f"에러: {e}\n")
    
    # 14. people_in_photo 테스트
    print("14. people_in_photo 테스트")
    try:
        result = tools.execute_tool(
            "14",
            photo_id="65f1234567890abcdef12345"  # 더미 photo_id
        )
        print(f"결과: {result}\n")
    except Exception as e:
        print(f"에러: {e}\n")
    
    # 16. get_person_by_id 테스트
    print("16. get_person_by_id 테스트")
    try:
        result = tools.execute_tool(
            "16",
            person_id="65f1234567890abcdef12345"  # 더미 person_id
        )
        print(f"결과: {result}\n")
    except Exception as e:
        print(f"에러: {e}\n")
    
    # 17. get_all_people 테스트
    print("17. get_all_people 테스트")
    try:
        result = tools.execute_tool("17")
        print(f"결과: {result}\n")
    except Exception as e:
        print(f"에러: {e}\n")

<<<<<<< HEAD
# 더미 데이터 추가
print("=== 더미 데이터 추가 ===")
result = service.add_person_to_photo(test_photo_id, test_person_id)
print(f"추가된 데이터: {result}")

# 특정 사람이 포함된 사진 검색
print("\n=== 특정 사람이 포함된 사진 검색 ===")
photos = service.get_photos_by_person(test_person_id)
print(f"검색된 사진 수: {len(photos)}")
for photo in photos:
    print(f"사진 ID: {photo.get('photoId')}")
    print(f"사람 ID: {photo.get('personId')}")

# 특정 사진에 포함된 사람 검색
print("\n=== 특정 사진에 포함된 사람 검색 ===")
people = service.get_people_in_photo(test_photo_id)
print(f"검색된 사람 수: {len(people)}")
for person in people:
    print(f"사진 ID: {person.get('photoId')}")
    print(f"사람 ID: {person.get('personId')}")
>>>>>>> d1e9136 (fixed error and functions in tools-photo-peoleservice)
=======
if __name__ == "__main__":
    test_all_tools()
>>>>>>> e0c7e6b (middle update)
