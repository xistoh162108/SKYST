from flask import Flask, request, jsonify
from bson import ObjectId
import json
from db.people import PeopleRepository
from db.photos import PhotoRepository
from db.photo_people import PhotoPeopleRepository
from db.photo_tags import PhotoTagsRepository
from db.huggingface.huggingface_tag import get_tags_from_huggingface

app = Flask(__name__)
people_repo = PeopleRepository()
photo_repo = PhotoRepository()
photo_people_repo = PhotoPeopleRepository()
photo_tags_repo = PhotoTagsRepository()

def serialize_id(doc):
    doc["_id"] = str(doc["_id"])
    return doc

@app.route("/api/people", methods=["GET"])
def get_people():
    people = people_repo.get_person({})
    result = [{
        "name": person["name"],
        "personId": str(person["_id"])}for person in people]
    return jsonify(result)

@app.route("/api/people", methods=["POST"])
def add_person():
    data = request.get_json()
    print(data)
    result = people_repo.add_person({"_id": data["id"], "name": data["name"]})
    return jsonify(result)

@app.route("/api/photos", methods=["GET"])
def get_photos_by_person():
    person_id = request.args.get("personId")
    query = {}
    if person_id:
        query["people"] = ObjectId(person_id)
    photos = photo_repo.get_photo(query)
    result = [{
        "id": str(photo["_id"]),
        "url": photo.get("image_url", ""),
        "location": photo.get("location", [])}for photo in photos]
    return jsonify(result)

@app.route("/api/photos", methods=["POST"])
def add_photo():
    img_file = request.files["img"]

    # 문자열로 전달된 JSON 데이터 파싱
    description = request.form.get("text", "")
    location = json.loads(request.form.get("location", "[]"))
    travel_id = request.form.get("travelId")
    people_ids = json.loads(request.form.get("peopleId", "[]"))

    # 예시 이미지 URL
    image_url = "hello"

    photo = {
        "image_url": image_url,
        "description": description,
        "location": location,
        "travel_id": travel_id
    }

    photo_id = photo_repo.add_photo(photo)

    photo_tags = get_tags_from_huggingface(img_file)

    for p in people_ids:
        photo_people_repo.add_photoPeople({
            "photoId": photo_id,
            "personId": p
        })

    for t in photo_tags:
        photo_tags_repo.add_photoTags({
            "photoId": photo_id,
            "tags": t
        })

    return {"photoId": str(photo_id)}, 201


@app.route("/api/photos/<photoId>", methods=["GET"])
def get_photo_detail(photoId):
    photo = photo_repo.get_photo({"_id": ObjectId(photoId)})
    photo = photo[0]

    people_raw = photo_people_repo.get_photoPeople({"photoId": ObjectId(photoId)})
    people = [str(p["personId"]) for p in people_raw]

    tags_raw = photo_tags_repo.get_photoTags({"photoId": ObjectId(photoId)})
    tags = [t["tags"] for t in tags_raw]

    return jsonify({
        "url": photo.get("image_url", ""),
        "text": photo.get("description", ""),
        "peopleId": people,
        "tags": tags,
        "travelId": str(photo.get("travel_id", ""))
    })



@app.route("/api/photos/<photoId>", methods=["PUT"])
def update_photo(photoId):
    data = request.get_json()
    update = {}
    if "img" in data:
        update["image_url"] = data["img"]
    if "text" in data:
        update["description"] = data["text"]
    if "peopleId" in data:
        photo_people_repo.delete_photoPeople({
            photoId: photoId
        })

        for p in data["peopleId"]:
            photo_people_repo.add_photoPeople({
                "photoId": photoId,
                "peopleId": ObjectId(p)
            })
        
    if "location" in data:
        update["location"] = data["location"]
    if "travelId" in data:
        update["travel_id"] = data["travelId"]
    if "tags" in data:
        photo_tags_repo.delete_photoTags({
            photoId: photoId
        })

        for pt in data["tags"]:
            photo_tags_repo.add_photoTags({
                "photoId": photoId,
                "tags": ObjectId(pt)
            })
        

    photo_repo.update_photo({"_id": ObjectId(photoId)}, {"$set": update})
    return

@app.route("/api/photos/<photoId>", methods=["DELETE"])
def delete_photo(photoId):
    photo_repo.delete_photo({"_id": ObjectId(photoId)})
    return

@app.route(";/api/recommend", methods=["POST"])
def recommend_photos():
    from flask import Flask, request, jsonify
from tools.tool import Tools
from llm.models import TOTPlanner, TOTExecutor
from db import PeopleRepository, PhotoRepository, PhotoPeopleRepository
import json
import traceback
import os

app = Flask(__name__)

# 데이터베이스 레포지토리 초기화
people_repo = PeopleRepository()
photo_repo = PhotoRepository()
photo_people_repo = PhotoPeopleRepository()

# Tools 인스턴스 생성
tools = Tools(
    photo_repo=photo_repo,
    people_repo=people_repo,
    photo_people_repo=photo_people_repo,
    enable_notes=True  # 노트 기능 활성화
)

# 환경 변수에서 API 키 가져오기
api_key = os.getenv("GOOGLE_API_KEY", "")

# TOT Planner와 Executor 초기화
tot_planner = TOTPlanner(api_key=api_key, tools=tools)
tot_executor = TOTExecutor(api_key=api_key, tools=tools)

@app.route('/api/recommend', methods=['POST'])
def recommend():
    """
    사용자 쿼리를 받아 TOT 계획을 생성하고 실행하여 추천 결과를 제공하는 API
    
    Request JSON:
    {
        "query": "사용자 질문/요청",
        "max_plans": 1  // 선택사항: 생성할 최대 계획 수 (기본값: 1)
    }
    
    Response JSON:
    {
        "success": true/false,
        "query": "원래 사용자 쿼리",
        "answer": "최종 답변",
        "details": {
            "plan": {...},  // 실행된 계획
            "summary": "실행 요약",
            "steps": [...],  // 각 단계별 결과
            "replan_count": 0  // 재계획 시도 횟수
        },
        "error": "오류 메시지 (실패 시)"
    }
    """
    try:
        # 요청 데이터 가져오기
        data = request.json
        
        if not data or 'query' not in data:
            return jsonify({
                "success": False,
                "error": "쿼리가 제공되지 않았습니다."
            }), 400
            
        query = data['query']
        max_plans = data.get('max_plans', 1)  # 기본값은 1개 계획
        
        # 입력 검증
        if not isinstance(query, str) or len(query.strip()) == 0:
            return jsonify({
                "success": False,
                "error": "유효한 쿼리가 아닙니다."
            }), 400
            
        if not isinstance(max_plans, int) or max_plans < 1:
            max_plans = 1
            
        # TOT 계획 생성 및 실행
        best_result = None
        best_score = -1
        all_plans = []
        
        for plan_idx in range(max_plans):
            try:
                # 계획 생성
                steps = tot_planner.build_full_plan(query)
                full_plan = {"steps": steps}
                all_plans.append(full_plan)
                
                # 계획 실행
                results = tot_executor.execute_plan(full_plan, query)
                
                # 계획 점수 계산 (성공적인 단계 비율)
                successful_steps = sum(1 for step in results.get('steps', []) 
                                     if step.get('analysis', {}).get('is_sufficient', False))
                total_steps = len(results.get('steps', []))
                
                score = successful_steps / total_steps if total_steps > 0 else 0
                
                # 더 나은 결과가 있으면 업데이트
                if score > best_score:
                    best_score = score
                    best_result = results
            except Exception as e:
                # 이 계획 실패, 다음 계획으로 진행
                print(f"계획 {plan_idx} 실행 중 오류: {str(e)}")
                continue
        
        # 모든 계획이 실패한 경우
        if best_result is None:
            return jsonify({
                "success": False,
                "query": query,
                "error": "모든 계획 실행에 실패했습니다."
            }), 500
            
        # 응답 구성
        final_answer = best_result.get('final_answer')
        
        # 노트 기반 답변이 없는 경우 기본 최종 요약 사용
        if final_answer is None or final_answer == "":
            final_answer = best_result.get('final_summary', "요청에 대한 답변을 생성할 수 없습니다.")
            
        response = {
            "success": True,
            "query": query,
            "answer": final_answer,
            "details": {
                "plan": best_result.get('final_plan', all_plans[0] if all_plans else {}),
                "summary": best_result.get('final_summary', ""),
                "steps": [
                    {
                        "description": step.get('step', {}).get('description', ""),
                        "tool_name": step.get('step', {}).get('tool_name', ""),
                        "summary": step.get('summary', ""),
                        "is_sufficient": step.get('analysis', {}).get('is_sufficient', False)
                    } for step in best_result.get('all_attempts', [])
                ],
                "replan_count": best_result.get('replan_count', 0)
            }
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        # 예외 처리
        print(f"API 처리 중 오류: {str(e)}")
        print(traceback.format_exc())
        
        return jsonify({
            "success": False,
            "query": request.json.get('query', ""),
            "error": str(e)
        }), 500

if __name__ == '__main__':
    # 개발 환경에서 실행
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    app.run(debug=True)
