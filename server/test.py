from db import PeopleRepository, PhotoRepository

def main():
    people_repo = PeopleRepository(db_name="skyst")
    photo_repo = PhotoRepository(db_name="skyst")

    print("=== People CRUD Operations ===")
    # Add person
    add_result = people_repo.add_person({"name": "Test User", "age": 99})
    print(f"Added person ID: {add_result.inserted_id}")

    # Read people
    people = people_repo.get_person({})
    print(f"People in DB: {people}")

    # Update person
    update_result = people_repo.update_person({"_id": add_result.inserted_id}, {"$set": {"age": 100}})
    print(f"People updated count: {update_result.modified_count}")

    # Delete person
    delete_result = people_repo.delete_person({"_id": add_result.inserted_id})
    print(f"People deleted count: {delete_result.deleted_count}")

    print("\n=== Photo CRUD Operations ===")
    # Add photo
    add_photo_result = photo_repo.add_photo({"url": "http://example.com/photo.jpg", "tags": ["test"]})
    print(f"Added photo ID: {add_photo_result.inserted_id}")

    # Read photos
    photos = photo_repo.get_photo({})
    print(f"Photos in DB: {photos}")

    # Update photo
    update_photo_result = photo_repo.update_photo({"_id": add_photo_result.inserted_id}, {"$set": {"tags": ["production"]}})
    print(f"Photos updated count: {update_photo_result.modified_count}")

    # Delete photo
    delete_photo_result = photo_repo.delete_photo({"_id": add_photo_result.inserted_id})
    print(f"Photos deleted count: {delete_photo_result.deleted_count}")

if __name__ == "__main__":
    main()