from db.photo_people import PhotoPeopleRepository
from tools.people_photo import PeoplePhotoService
    
    # 레포지토리와 서비스 인스턴스 생성
photo_people_repo = PhotoPeopleRepository()
service = PeoplePhotoService(photo_people_repo)

# 테스트용 더미 데이터 생성
test_photo_id = "65f1234567890abcdef12345"  # 테스트용 photo_id
test_person_id = "65f0987654321fedcba09876"  # 테스트용 person_id

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