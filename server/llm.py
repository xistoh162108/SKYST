from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from dotenv import load_dotenv
import os

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
        
        # 대화 메모리 초기화
        self.memory = ConversationBufferMemory()
        
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
        self.memory = ConversationBufferMemory()
        self.conversation = ConversationChain(
            llm=self.llm,
            memory=self.memory,
            verbose=True
        )

def main():
    # LLM 인스턴스 생성
    llm = GeminiLLM()
    
    # 시스템 프롬프트 설정 (선택사항)
    system_prompt = "당신은 친절하고 도움이 되는 AI 어시스턴트입니다."
    
    # 예시 프롬프트
    prompt = "인공지능에 대해 간단히 설명해주세요."
    
    # 응답 생성
    response = llm.generate_response(prompt, system_prompt)
    print(f"시스템 프롬프트: {system_prompt}")
    print(f"사용자 프롬프트: {prompt}")
    print(f"응답: {response}")

if __name__ == "__main__":
    main() 