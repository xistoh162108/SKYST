from flask import Flask, request, jsonify
from bson import ObjectId
from server.db.people import PeopleRepository
from server.db.photos import PhotoRepository

app = Flask(__name__)
people_repo = PeopleRepository()
photo_repo = PhotoRepository()

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
        "people": [ObjectId(p) for p in data.get("peopleId", [])],
        "location": data.get("location", []),
        "travel_id": data.get("travelId")
    }
    photo_repo.add_photo(photo)
    return

@app.route("/api/photos/<photo_id>", methods=["GET"])
def get_photo_detail(photo_id):
    photo = photo_repo.get_photo({"_id": ObjectId(photo_id)})
    if not photo:
        return jsonify({"error": "Not found"}), 404
    photo = photo[0]
    return jsonify({
        "text": photo.get("description", ""),
        "personId": [str(p) for p in photo.get("people", [])]
    })

@app.route("/api/photos/<photo_id>", methods=["PUT"])
def update_photo(photo_id):
    data = request.get_json()
    update = {}
    if "text" in data:
        update["description"] = data["text"]
    if "people" in data:
        update["people"] = [ObjectId(p) for p in data["people"]]
    if "location" in data:
        update["location"] = data["location"]
    photo_repo.update_photo({"_id": ObjectId(photo_id)}, {"$set": update})
    return jsonify({"message": "photo updated"})

@app.route("/api/photos/<photo_id>", methods=["DELETE"])
def delete_photo(photo_id):
    try:
        result = photo_repo.delete_photo({"_id": ObjectId(photo_id)})
        if result.deleted_count == 0:
            return jsonify({"error": "Photo not found"}), 404
        return jsonify({"message": "Photo deleted"})
    except Exception:
        return jsonify({"error": "Invalid photoId"}), 400

if __name__ == "__main__":
    app.run(debug=True)
