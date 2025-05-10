from flask import Flask, request, jsonify
from bson import ObjectId
from server.db.people import PeopleRepository
from server.db.photos import PhotoRepository
from server.db.photo_people import PhotoPeopleRepository
from server.db.photo_tags import PhotoTagsRepository

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
    people_repo.add_person({"_id": data["id"], "name": data["name"]})
    return

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
    data = request.get_json()

    #image_url = get_image_url(img)
    # 이미지 클라우드에 업로드 해서 img 링크 받아오는 함수
    image_url = "hello"

    photo = {
        "image_url": image_url,
        "description": data.get("text", ""),
        "location": data.get("location", []),
        "travel_id": data.get("travelId")
    }

    photo_id = photo_repo.add_photo(photo)
    #photo_tags = getTags(image_url)
    # 이미지 태그 추출해주는 함수
    photo_tags = ["hello", "NUBZUKNUBZUK"]

    for p in data["peopleId"]:
        photo_people_repo.add_photoPeople({
            "photoId": photo_id,
            "personId": ObjectId(p) # 안뇽
        })

    return {"photoId": str(photo_id)}, 201

@app.route("/api/photos/<photoId>", methods=["GET"])
def get_photo_detail(photoId):
    photo = photo_repo.get_photo({"_id": ObjectId(photoId)})
    photo = photo[0]

    people = photo_people_repo.get_photoPeople({ photoId })
    tags = photo_tags_repo.get_photoTags({ photoId })

    return jsonify({
        "url": photo.get("image_url", ""),
        "text": photo.get("description", ""),
        "peopleId": people,
        tags: tags,
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
