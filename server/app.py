from flask import Flask, request, jsonify
from bson import ObjectId
import json
from db.people import PeopleRepository
from db.photos import PhotoRepository
from db.photo_people import PhotoPeopleRepository
from db.photo_tags import PhotoTagsRepository
from db.huggingface.huggingface_tag import get_tags_from_huggingface
from db.travel_people import TravelPeopleRepository
from db.travel_places import TravelPlacesRepository
from db.travel import TravelRepository
import os
from tools.tool import Tools
from llm.models import TOTPlanner, TOTExecutor
app = Flask(__name__)
people_repo = PeopleRepository()
photo_repo = PhotoRepository()
photo_people_repo = PhotoPeopleRepository()
photo_tags_repo = PhotoTagsRepository()
travel_people_repo = TravelPeopleRepository()
travel_places_repo = TravelPlacesRepository()
travel_repo = TravelRepository()
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




# New route: Get 5 most recent travels and their places
@app.route("/api/travels", methods=["GET"])
def get_recent_travels():
    """
    Returns the 5 most recent travels and their associated places.

    Response Body Example:
    [
        {
            "id": str,
            "date": date,
            "name": str,
            "places": [
                {
                    "name": str,
                    "order": int
                }
            ]
        }
    ]
    """

    try:
        # Fetch all travels, then sort by date descending and take the latest five
        travels = travel_repo.get_travel({})
        travels_sorted = sorted(
            travels, key=lambda t: t.get("date", ""), reverse=True
        )[:5]

        response = []
        for travel in travels_sorted:
            travel_id = travel["_id"]

            # Retrieve places linked to this travel
            places_raw = travel_places_repo.get_travel_place({"travelId": travel_id})

            # Build places list, preserving 'order' field if present
            places = []
            for idx, place in enumerate(places_raw):
                places.append({
                    "name": place.get("placeId", ""),
                    "order": place.get("order", idx)
                })

            response.append({
                "id": str(travel_id),
                "date": travel.get("date"),
                "name": travel.get("name", ""),
                "places": places
            })

        return jsonify(response), 200
    except Exception as e:
        # Return a 400 with error details if something goes wrong
        return jsonify({"error": str(e)}), 400



# New route: Get a detailed travel record
@app.route("/api/travels/<travelId>", methods=["GET"])
def get_travel_detail(travelId):
    """
    Returns detailed information for a single travel.

    Response Body Example:
    {
        "date": date,
        "people": [
            { "id": str, "name": str }
        ],
        "name": str,
        "places": [
            {
                "id": str,
                "order": int,
                "name": str,
                "location": list
            }
        ]
    }
    """
    try:
        # Validate ObjectId
        if not ObjectId.is_valid(travelId):
            return jsonify({"error": "Invalid travelId"}), 400

        # Fetch the travel document
        travel_docs = travel_repo.get_travel({"_id": ObjectId(travelId)})
        if not travel_docs:
            return jsonify({"error": "Invalid travelId"}), 400
        travel = travel_docs[0]

        # ---- People Section ----
        people_links = travel_people_repo.get_travel_person({"travelId": ObjectId(travelId)})
        people_list = []
        for link in people_links:
            pid = link.get("peopleId")
            person_name = ""
            # Attempt to resolve the person's name if we have a valid ObjectId
            try:
                if ObjectId.is_valid(str(pid)):
                    person_docs = people_repo.get_person({"_id": ObjectId(pid)})
                    if person_docs:
                        person_name = person_docs[0].get("name", "")
            except Exception:
                pass  # In case pid is not an ObjectId or repository fails
            people_list.append({
                "id": str(pid),
                "name": person_name
            })

        # ---- Places Section ----
        place_links = travel_places_repo.get_travel_place({"travelId": ObjectId(travelId)})
        places_output = []
        for idx, link in enumerate(place_links):
            place_id = link.get("placeId", "")
            order_val = link.get("order", idx)

            # Try to infer location via photos of this travel having non-empty 'location'
            location_val = []
            try:
                photos = photo_repo.get_photo({
                    "travel_id": ObjectId(travelId),
                    "location": {"$ne": []}
                })
                # Pick first photo's location if available
                if photos:
                    location_val = photos[0].get("location", [])
            except Exception:
                pass

            places_output.append({
                "id": place_id,
                "order": order_val,
                "name": place_id,     # using place_id as name fallback
                "location": location_val
            })

        response = {
            "date": travel.get("date"),
            "people": people_list,
            "name": travel.get("name", ""),
            "places": places_output
        }
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# New route: Update a travel record
@app.route("/api/travels/<travelId>", methods=["PUT"])
def update_travel(travelId):
    """
    Updates an existing travel record.

    Expected JSON body (all fields optional):
    {
        "date": "YYYY-MM-DD",
        "peopleId": ["<personId>", ...],
        "name": "<travel name>",
        "places": [
            {
                "id": "<placeId>",
                "order": <int>
            }
        ]
    }

    Returns 200 on success, 400 on invalid input.
    """
    try:
        # Validate travelId
        if not ObjectId.is_valid(travelId):
            return jsonify({"error": "Invalid travelId"}), 400

        data = request.get_json(force=True)
        if data is None:
            data = {}

        # -- Update basic fields in the travel document --
        update_doc = {}
        if "name" in data:
            update_doc["name"] = data["name"]
        if "date" in data:
            update_doc["date"] = data["date"]
        if update_doc:
            travel_repo.update_travel({"_id": ObjectId(travelId)}, {"$set": update_doc})

        # -- Update people links --
        if "peopleId" in data:
            # Remove existing links
            travel_people_repo.delete_travel_person({"travelId": ObjectId(travelId)})
            # Add new links
            for pid in data["peopleId"]:
                try:
                    travel_people_repo.add_travel_person({
                        "travelId": ObjectId(travelId),
                        "peopleId": ObjectId(pid)
                    })
                except Exception:
                    travel_people_repo.add_travel_person({
                        "travelId": ObjectId(travelId),
                        "peopleId": pid
                    })

        # -- Update places links --
        if "places" in data:
            travel_places_repo.delete_travel_place({"travelId": ObjectId(travelId)})
            for place in data["places"]:
                travel_places_repo.add_travel_place({
                    "travelId": ObjectId(travelId),
                    
                    "placeId": place.get("id"),
                    "order": place.get("order")
                })

        return "", 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# New route: Delete a travel record
@app.route("/api/travels/<travelId>", methods=["DELETE"])
def delete_travel(travelId):
    """
    Deletes a travel record and its linked people/places documents.

    Response Codes:
        200 – Succeed
        400 – Invalid travelId
    """
    try:
        # Validate ObjectId
        if not ObjectId.is_valid(travelId):
            return jsonify({"error": "Invalid travelId"}), 400

        travel_oid = ObjectId(travelId)

        # Remove travel document
        travel_repo.delete_travel({"_id": travel_oid})

        # Remove associated people and places links
        travel_people_repo.delete_travel_person({"travelId": travel_oid})
        travel_places_repo.delete_travel_place({"travelId": travel_oid})

        return "", 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# New route: Upload a travel record
@app.route("/api/travels/post", methods=["POST"])
def create_travel():
    """
    Creates a new travel record with associated people and places.

    Expected JSON body:
    {
        "date": "YYYY-MM-DD",
        "peopleId": ["<personId>", ...],
        "name": "<travel name>",
        "places": [
            {
                "id": "<placeId>",
                "order": <int>
            }
        ]
    }

    Returns the created travel data on success.
    """
    try:
        data = request.get_json(force=True)

        # Validate input
        name = data.get("name")
        date = data.get("date")
        people_ids = data.get("peopleId", [])
        places = data.get("places", [])

        if not name or not date:
            return jsonify({"error": "Both 'name' and 'date' are required."}), 400

        # Insert travel document
        travel_id = travel_repo.add_travel({
            "name": name,
            "date": date
        })

        # Link people to the travel
        for pid in people_ids:
            try:
                travel_people_repo.add_travel_person({
                    "travelId": travel_id,
                    "peopleId": ObjectId(pid)
                })
            except Exception:
                # If pid is not a valid ObjectId, store as raw string
                travel_people_repo.add_travel_person({
                    "travelId": travel_id,
                    "peopleId": pid
                })

        # Link places to the travel
        for place in places:
            travel_places_repo.add_travel_place({
                "travelId": travel_id,
                "placeId": place.get("id"),
                "order": place.get("order")
            })

        response = {
            "id": str(travel_id),
            "date": date,
            "peopleId": people_ids,
            "name": name,
            "places": places
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ---------------------------------------------------------------------------
# New route: Recommend places based on a prompt and selected people
@app.route("/api/recommend", methods=["POST"])
def recommend_places():
    """
    Generates place recommendations using a TOT pipeline.

    Query Parameters (POST form or query‑string):
        prompt (str)      – The natural‑language prompt.
        peopleId (list)   – Repeated peopleId parameters or a comma‑separated string.

    Success Response (200):
    {
        "places": [
            {
                "id": str,
                "order": int,
                "name": str,
                "location": list
            }
        ]
    }

    Error Response (400) – malformed peopleId or internal failure.
    """
    # --- 1) Retrieve parameters ------------------------------------------------
    prompt = request.args.get("prompt") or request.form.get("prompt", "")
    people_ids = request.args.getlist("peopleId") or request.form.getlist("peopleId")

    # Fallback to JSON body if provided
    if not prompt or not people_ids:
        data = request.get_json(silent=True) or {}
        prompt = prompt or data.get("prompt", "")
        people_ids = people_ids or data.get("peopleId", [])

    # Basic validation
    if not prompt:
        return jsonify({"error": "prompt is required"}), 400
    if isinstance(people_ids, str):
        people_ids = [pid.strip() for pid in people_ids.split(",") if pid.strip()]
    if not isinstance(people_ids, list):
        return jsonify({"error": "Invalid peopleId"}), 400

    # --- 2) Build TOT pipeline -------------------------------------------------
    try:
        tools = Tools(
            photo_repo=photo_repo,
            people_repo=people_repo,
            photo_people_repo=photo_people_repo
        )
        planner = TOTPlanner(api_key=os.getenv("GOOGLE_API_KEY", ""), tools=tools)
        executor = TOTExecutor(api_key=os.getenv("GOOGLE_SEARCH_CX", ""), tools=tools)

        # Build and execute a single TOT plan
        steps = planner.build_full_plan(prompt)
        plan = {"steps": steps}
        results = executor.execute_plan(plan, prompt)

        # --- 3) Extract recommended places ------------------------------------
        recommended_places = []
        # Try to locate a "places" list either in step results or final summary
        for step in results.get("steps", []):
            res = step.get("result", {})
            if isinstance(res, dict) and "places" in res:
                recommended_places = res["places"]
                break
        if not recommended_places and isinstance(results.get("final_summary"), dict):
            recommended_places = results["final_summary"].get("places", [])

        # Normalise output shape
        formatted = []
        for idx, place in enumerate(recommended_places):
            formatted.append({
                "id": str(place.get("id", "")),
                "order": int(place.get("order", idx)),
                "name": place.get("name", ""),
                "location": place.get("location", [])
            })

        return jsonify({"places": formatted}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
