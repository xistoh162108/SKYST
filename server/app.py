from flask import Flask, request, jsonify
from bson import ObjectId
from server.db.people import PeopleRepository
from server.db.photos import PhotoRepository
from server.db.photo_people import PhotoPeopleRepository

app = Flask(__name__)
people_repo = PeopleRepository()
photo_repo = PhotoRepository()
photo_people_repo = PhotoPeopleRepository()

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
    photo = {
        "image_url": data["img"],
        "description": data.get("text", ""),
        "location": data.get("location", []),
        "travel_id": data.get("travelId")
    }

    photo_id = photo_repo.add_photo(photo)

    for p in data["peopleId"]:
        photo_people_repo.add_photoPeople({
            "photoId": photo_id,
            "personId": ObjectId(p)
        })

    return {"photoId": str(photo_id)}, 201

@app.route("/api/photos/<photoId>", methods=["GET"])
def get_photo_detail(photoId):
    photo = photo_repo.get_photo({"_id": ObjectId(photoId)})
    photo = photo[0]
    return jsonify({
        "url": photo.get("image_url", ""),
        "text": photo.get("description", ""),
        "peopleId": [str(p) for p in photo.get("people", [])],
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
        update["people"] = [ObjectId(p) for p in data["peopleId"]]
    if "location" in data:
        update["location"] = data["location"]
    if "travelId" in data:
        update["travel_id"] = data["travelId"]
    photo_repo.update_photo({"_id": ObjectId(photoId)}, {"$set": update})
    return

@app.route("/api/photos/<photoId>", methods=["DELETE"])
def delete_photo(photoId):
    photo_repo.delete_photo({"_id": ObjectId(photoId)})
    return

if __name__ == "__main__":
    app.run(debug=True)
