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


class MongoDBClient:
    """
    MongoDB 연결과 CRUD 작업을 담당하는 클래스.
    사용 예시:
        client = MongoDBClient(db_name="mydb")
        client.create("images", {"key": "value"})
    """

    def __init__(
        self,
        db_name: str,
        host: str = "localhost",
        port: int = 27017,
        user: str = None,
        password: str = None
    ):
        # MongoDB URI 구성
        if user and password:
            uri = f"mongodb://{user}:{password}@{host}:{port}/{db_name}"
        else:
            uri = f"mongodb://{host}:{port}/{db_name}"

        # 클라이언트 및 DB 객체 생성
        self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        try:
            self.client.admin.command("ping")
        except ConnectionFailure:
            raise RuntimeError("MongoDB 서버에 연결할 수 없습니다.")
        self.db = self.client[db_name]

    def create(self, collection_name: str, data: dict):
        """단일 문서 삽입(Create)"""
        res = self.db[collection_name].insert_one(data)
        return res.inserted_id

    def read(self, collection_name: str, query: dict):
        """문서 조회(Read)"""
        return list(self.db[collection_name].find(query))

    def update(self, collection_name: str, query: dict, update_data: dict):
        """문서 수정(Update), update_data는 $set 형식으로 전달"""
        return self.db[collection_name].update_one(query, update_data)

    def delete(self, collection_name: str, query: dict):
        """문서 삭제(Delete)"""
        return self.db[collection_name].delete_one(query)
