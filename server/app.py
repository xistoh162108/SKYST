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

if __name__ == "__main__":
    app.run(debug=True)
