from flask import Flask, request, jsonify
from bson import ObjectId
import json
from db.people import PeopleRepository
from db.photos import PhotoRepository
from db.photo_people import PhotoPeopleRepository
from db.photo_tags import PhotoTagsRepository
from db.huggingface.huggingface_tag import get_tags_from_huggingface
from server.db.travel_people import TravelRepository
from db.travel_people import TravelPeopleRepository
from db.travel_places import TravelPlacesRepository
app = Flask(__name__)
people_repo = PeopleRepository()
photo_repo = PhotoRepository()
photo_people_repo = PhotoPeopleRepository()
photo_tags_repo = PhotoTagsRepository()
travel_repo = TravelRepository()
travel_people_repo = TravelPeopleRepository()
travel_places_repo = TravelPlacesRepository()
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

@app.route("/api/travels", methods=["GET"])
def get_travels():
    travels_raw = travel_repo.get_travel({})
    travels_sorted = sorted(travels_raw, key=lambda t: t.get("date", ""),
                            reverse=True)[:5]
    result = []
    for tr in travels_sorted:
        place_docs = travel_places_repo.get_travel_place({"travelId": tr["_id"]})
        places = sorted(
            [{"name": p.get("name", ""), "order": p.get("order", 99)} for p in place_docs],
            key=lambda x: x["order"]
        )
        result.append({
            "id": str(tr["_id"]),
            "date" : tr.get("date", ""),
            "name" : tr.get("name", ""),
            "places" : places
        })
    return jsonify(result), 200
    
@app.route("/api/travels", methods=["POST"])
def add_travel():
    data = request.get_json()
    if not data:
        return jsonify({"error": "empty body"}), 400

    required = ["date", "name"]
    missing = [k for k in required if k not in data]
    if missing:
        return jsonify({"error": f"missing required fields: {missing}"}), 400

    # 1) travels 컬렉션에 기본 문서 저장
    travel_doc = {
        "date": data["date"],
        "name": data["name"]
    }
    travel_id = travel_repo.add_travel(travel_doc)

    # 2) travels_people 매핑 저장
    for pid in data.get("peopleId", []):
        travel_people_repo.add_travel_person({
            "travelId": travel_id,
            "personId": ObjectId(pid)
        })

    # 3) travels_places 매핑 저장
    for idx, p in enumerate(data.get("places", [])):
        travel_places_repo.add_travel_place({
            "travelId": travel_id,
            "placeId": ObjectId(p["id"]),
            "order": p.get("order", idx + 1)
        })

    return jsonify({"travelId": str(travel_id)}), 200

@app.route("/api/travels/<travelId>", methods=["GET"])
def get_travel_detail(travelId):
    """
    여행 상세 기록 가져오기
    Response 예:
    {
        "date": "2025-05-12",
        "people": [
            { "id": "...", "name": "지민" }, ...
        ],
        "name": "제주 가족 여행",
        "places": [
            { "id": "...", "order": 1, "name": "성산 일출봉", "location": [33.45, 126.93] },
            ...
        ]
    }
    """
    try:
        travel_oid = ObjectId(travelId)
    except Exception:
        return jsonify({"error": "Invalid travelId"}), 400

    travels = travel_repo.get_travel({"_id": travel_oid})
    if not travels:
        return jsonify({"error": "Invalid travelId"}), 400

    tr = travels[0]

    # people 목록
    people_raw = travel_people_repo.get_travel_person({"travelId": travel_oid})
    people_list = []
    for pr in people_raw:
        pid = pr["personId"]
        person_docs = people_repo.get_person({"_id": pid})
        name = person_docs[0]["name"] if person_docs else ""
        people_list.append({"id": str(pid), "name": name})

    # places 목록
    places_raw = travel_places_repo.get_travel_place({"travelId": travel_oid})
    places_list = []
    for pr in places_raw:
        places_list.append({
            "id": str(pr["placeId"]),
            "order": pr.get("order", 0),
            "name": pr.get("name", ""),
            "location": pr.get("location", [])
        })

    return jsonify({
        "date": tr.get("date", ""),
        "people": people_list,
        "name": tr.get("name", ""),
        "places": places_list
    }), 200


# 여행 정보 수정
@app.route("/api/travels/<travelId>", methods=["PUT"])
def update_travel(travelId):
    """
    여행 정보 수정
    Body 예:
    {
        "date": "2025-05-13",
        "peopleId": ["6089...", "60ab..."],
        "name": "수정된 여행 이름",
        "places": [
            { "id": "64cd...", "order": 1 },
            { "id": "64ce...", "order": 2 }
        ]
    }
    """
    try:
        travel_oid = ObjectId(travelId)
    except Exception:
        return jsonify({"error": "Invalid travelId"}), 400

    data = request.get_json()
    if not data:
        return jsonify({"error": "empty body"}), 400

    # build $set update dict only with provided fields
    update_fields = {}
    if "date" in data:
        update_fields["date"] = data["date"]

    if "name" in data:
        update_fields["name"] = data["name"]

    if "peopleId" in data:
        update_fields["people"] = [ObjectId(pid) for pid in data["peopleId"]]

    if "places" in data:
        update_fields["places"] = [
            {
                "placeId": ObjectId(p["id"]),
                "order": p.get("order", idx + 1)
            }
            for idx, p in enumerate(data["places"])
        ]

    if "peopleId" in data:
        # Delete old mapping then add new
        travel_people_repo.delete_travel_person({"travelId": travel_oid})
        for pid in data["peopleId"]:
            travel_people_repo.add_travel_person({"travelId": travel_oid, "personId": ObjectId(pid)})

    if "places" in data:
        travel_places_repo.delete_travel_place({"travelId": travel_oid})
        for idx, p in enumerate(data["places"]):
            travel_places_repo.add_travel_place({
                "travelId": travel_oid,
                "placeId": ObjectId(p["id"]),
                "order": p.get("order", idx + 1)
            })

    if not update_fields:
        return jsonify({"error": "no updatable fields"}), 400

    # perform update
    travel_repo.update_travel({"_id": travel_oid}, {"$set": update_fields})

    return jsonify({"message": "updated"}), 200


# 여행 기록 삭제
@app.route("/api/travels/<travelId>", methods=["DELETE"])
def delete_travel(travelId):
    """
    여행 기록 삭제
    성공 시 200, travelId 오류 시 400
    """
    try:
        travel_oid = ObjectId(travelId)
    except Exception:
        return jsonify({"error": "Invalid travelId"}), 400

    deleted = travel_repo.delete_travel({"_id": travel_oid})
    if not deleted:
        return jsonify({"error": "Invalid travelId"}), 400

    travel_people_repo.delete_travel_person({"travelId": travel_oid})
    travel_places_repo.delete_travel_place({"travelId": travel_oid})

    return jsonify({"message": "deleted"}), 200


if __name__ == "__main__":
    app.run(debug=True)
