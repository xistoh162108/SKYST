from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from dotenv import load_dotenv
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from langchain.chat_memory import MongoDBChatMessageHistory

def get_database(
    db_name: str,
    host: str = "localhost",
    port: int = 27017,
    user: str = None,
    password: str = None
):
    """
    MongoDB에 연결하고, db_name 데이터베이스 객체를 반환합니다.
    user/password를 넣으면 인증 연결을, 아니면 로컬 연결을 수행합니다.
    """
    if user and password:
        uri = f"mongodb://{user}:{password}@{host}:{port}/"
    else:
        uri = f"mongodb://{host}:{port}/"

    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    try:
        client.admin.command("ping")
    except ConnectionFailure:
        raise RuntimeError("❌ MongoDB 서버에 연결할 수 없습니다.")
    return client[db_name]

# .env 파일에서 환경 변수 로드
load_dotenv()

class GeminiLLM:
    def __init__(self, model_name="gemini-2.5-flash-preview-04-17"):
        """
        Gemini LLM 초기화
        :param model_name: 사용할 모델 이름 (기본값: gemini-2.5-flash-preview-04-17)
        """
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0.7,
            max_output_tokens=10000,
            google_api_key=os.getenv('GOOGLE_API_KEY')
        )
        
        # Initialize MongoDB-backed message history instead of in-memory buffer
        db = get_database(os.getenv("MONGODB_DB", "chat_history"))
        history_collection = db[os.getenv("MONGODB_COLLECTION", "messages")]
        self.memory = MongoDBChatMessageHistory(
            database=db,
            collection_name=os.getenv("MONGODB_COLLECTION", "messages")
        )
        
        # 대화 체인 초기화
        self.conversation = ConversationChain(
            llm=self.llm,
            memory=self.memory,
            verbose=True
        )

    def generate_response(self, prompt, system_prompt=None):
        """
        프롬프트에 대한 응답 생성
        :param prompt: 입력 프롬프트
        :param system_prompt: 시스템 프롬프트 (선택사항)
        :return: 생성된 응답
        """
        try:
            # 시스템 프롬프트가 있는 경우 메모리에 추가
            if system_prompt:
                self.memory.chat_memory.add_message(
                    SystemMessage(content=system_prompt)
                )
            
            # 응답 생성
            response = self.conversation.predict(input=prompt)
            return response
            
        except Exception as e:
            return f"에러 발생: {str(e)}"

    def reset_chat(self):
        """채팅 히스토리 초기화"""
        db = get_database(os.getenv("MONGODB_DB", "chat_history"))
        self.memory = MongoDBChatMessageHistory(
            database=db,
            collection_name=os.getenv("MONGODB_COLLECTION", "messages")
        )
        self.conversation = ConversationChain(
            llm=self.llm,
            memory=self.memory,
            verbose=True
        )