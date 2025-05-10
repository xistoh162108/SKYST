from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

def get_database(
    db_name: str,
    host: str = "localhost",
    port: int = 27017,
    user: str = None,
    password: str = None
):
    if user and password:
        uri = f"mongodb://{user}:{password}@{host}:{port}/{db_name}"
    else:
        uri = f"mongodb://{host}:{port}/{db_name}"

    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    
    try:
        client.admin.command("ping")
    except ConnectionFailure:
        raise RuntimeError("MongoDB 서버에 연결할 수 없습니다.")
    
    return client[db_name]

def main():
    db = get_database("skyst")
    collection = db["images"]
    
     # —— Create (삽입) ——
    doc = {"name": "홍길동", "age": 25, "skills": ["Python", "MongoDB"]}
    insert_result = collection.insert_one(doc)
    print("Inserted ID:", insert_result.inserted_id)
    
    # —— Read (조회) ——
    one = collection.find_one({"name": "홍길동"})
    print("Find one:", one)
    
    many = list(collection.find({"age": {"$gte": 20}}))
    print("Find many:", many)
    print("hello")
    
    # —— Update (수정) ——
    update_result = collection.update_one(
        {"name": "홍길동"},
        {"$set": {"age": 26}}
    )
    print("Matched:", update_result.matched_count,
          "Modified:", update_result.modified_count)
    
    # —— Delete (삭제) ——
    delete_result = collection.delete_one({"name": "홍길동"})
    print("Deleted:", delete_result.deleted_count)

if __name__ == "__main__":
    main()
