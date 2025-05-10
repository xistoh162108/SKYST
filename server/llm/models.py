# utils/models.py

from typing import Any, Dict, Tuple
from utils.prompt import InstructionConfig
from utils.chatbot import ChatBot
from utils.chain import LLMChain

class InputChecker:
    """
    사용자가 입력한 텍스트가 여행 경로 추천 요청에 해당하는지 판별합니다.
    내부적으로 'purpose_check_chain' 과 동일한 프롬프트와 체인을 사용합니다.
    """

    def __init__(self):
        # 1) 프롬프트 설정 with few-shot examples
        self.prompt = InstructionConfig(
            instruction=(
                "사용자의 다음 질문이 여행 경로 추천 요청과 관련된지 판단하세요. 관련 있으면 'yes', 아니면 'no'라고 답해주세요.\n\n여행 계획: {query}"
            ),
            input_variables=["query"],
            examples=[
                {"query": "친구와 다음 달 제주도 3박4일 여행 코스 추천해줘", "purpose_check": "yes"},
                {"query": "서울 날씨 알려줘", "purpose_check": "no"}
            ]
        )

        # 2) ChatBot 생성: 시스템 메시지는 상담 여부 판단 전문가로 설정
        self.chatbot = ChatBot(
            system_instruction="당신은 심리 상담 관련 질문인지 여부를 판단하는 전문가입니다."
        )

        # 3) LLMChain 구성 with updated output_key
        self.chain = LLMChain(
            chatbot=self.chatbot,
            prompt=self.prompt,
            output_key="purpose_check"
        )

    def is_travel_request(self, text: str) -> Tuple[bool, str]:
        """
        입력 텍스트가 여행 경로 추천 요청이면 (True, refined_prompt), 아니면 (False, None)를 반환합니다.
        """
        result = self.chain.run({"query": text})
        answer = result.get("purpose_check", "").strip().lower()
        if answer == "yes":
            refined_prompt = self.refine_prompt(text)
            return True, refined_prompt
        else:
            return False, None

    def refine_prompt(self, text: str) -> str:
        """
        주어진 여행 요청 문장에서 핵심 정보를 추출하여, '누구와', '어디를', '언제'를 포함한 문장으로 정제하세요.
        """
        refine_prompt_config = InstructionConfig(
            instruction=(
                "주어진 여행 요청 문장에서 핵심 정보를 추출하여, '누구와', '어디를', '언제'를 포함한 문장으로 정제하세요.\n\n원본 요청: {query}"
            ),
            input_variables=["query"]
        )

        refine_chatbot = ChatBot(system_instruction="Prompt Refiner")

        refine_chain = LLMChain(
            chatbot=refine_chatbot,
            prompt=refine_prompt_config,
            output_key="refined_travel_prompt"
        )

        result = refine_chain.run({"query": text})
        return result.get("refined_travel_prompt", "").strip()