from tools.tools import Tools
from llm.models import TOTPlanner, TOTExecutor
from db import PeopleRepository, PhotoRepository, PhotoPeopleRepository
import json

def create_test_data(photo_repo, people_repo, photo_people_repo):
    """테스트용 더미 데이터 생성"""
    # 사람 데이터 생성
    person_data = {
        "name": "홍길동",
        "birth_date": "1990-01-01",
        "gender": "male",
        "nationality": "KR",
        "metadata": {
            "height": 180,
            "weight": 70,
            "hair_color": "black",
            "eye_color": "brown"
        }
    }
    person_id = people_repo.add_person(person_data)
    print(f"생성된 person_id: {person_id}")

    # 사진 데이터 생성
    photo_data = {
        "file_path": "/test/path/photo1.jpg",
        "file_name": "photo1.jpg",
        "file_size": 1024,
        "file_type": "image/jpeg",
        "width": 1920,
        "height": 1080,
        "taken_at": "2024-03-20T10:00:00",
        "location": {
            "type": "Point",
            "coordinates": [126.9779692, 37.5662952]
        },
        "tags": ["여행", "바다", "가족"],
        "metadata": {
            "camera": "Canon EOS 5D",
            "exposure": "1/1000",
            "f_number": 2.8,
            "iso": 100
        }
    }
    photo_id = photo_repo.add_photo(photo_data)
    print(f"생성된 photo_id: {photo_id}")

    # 사진-사람 매핑 데이터 생성
    photo_people_data = {
        "photo_id": photo_id,
        "person_id": person_id,
        "face_location": {
            "x": 100,
            "y": 100,
            "width": 200,
            "height": 200
        },
        "confidence": 0.95
    }
    photo_people_repo.add_photoPeople(photo_people_data)

    return person_id, photo_id

def test_tot_pipeline():
    """TOT 생성 및 실행 파이프라인 테스트"""
    # 데이터베이스 레포지토리 초기화
    people_repo = PeopleRepository()
    photo_repo = PhotoRepository()
    photo_people_repo = PhotoPeopleRepository()

    # 테스트 데이터 생성
    person_id, photo_id = create_test_data(photo_repo, people_repo, photo_people_repo)

    # Tools 인스턴스 생성
    tools = Tools(
        photo_repo=photo_repo,
        people_repo=people_repo,
        photo_people_repo=photo_people_repo
    )

    # TOT Planner(계획)와 실행기 초기화
    planner = TOTPlanner(api_key="your_api_key", tools=tools)
    tot_executor = TOTExecutor(api_key="your_api_key", tools=tools)

    # 테스트할 쿼리 목록
    test_queries = [
        "서울에서 지민이랑 갈만한 맛있는 카페 추천해줘",
    ]

    # 각 쿼리에 대한 TOT 생성 및 실행
    for query in test_queries:
        print("\n" + "="*50)
        print(f"쿼리: {query}")
        print("="*50)
        
        try:
            for plan_idx in range(1, 4):   # 3개의 서로 다른 계획
                print(f"\n--- 계획 {plan_idx} / 3 ---")

                # 1. 전체 계획 생성
                print("\n1. TOT 계획 생성 중...")
                steps = planner.build_full_plan(query)
                full_plan = {"steps": steps}
                print("\n생성된 실행 계획:")
                print(json.dumps(full_plan, indent=2, ensure_ascii=False))

                # 2. TOT 실행
                print("\n2. TOT 실행 중...")
                results = tot_executor.execute_plan(full_plan)

                # 3. 실행 결과 출력
                print("\n실행 결과:")
                print("\n각 단계별 결과:")
                for idx, step_result in enumerate(results['steps'], 1):
                    print(f"\n단계 {idx}:")
                    print(f"결과: {json.dumps(step_result['result'], indent=2, ensure_ascii=False)}")
                    print(f"분석: {json.dumps(step_result['analysis'], indent=2, ensure_ascii=False)}")
                    print(f"요약: {step_result['summary']}")

                print("\n최종 요약:")
                print(results['final_summary'])
            
        except Exception as e:
            print(f"오류 발생: {str(e)}")
            import traceback
            print(traceback.format_exc())

if __name__ == "__main__":
    test_tot_pipeline()