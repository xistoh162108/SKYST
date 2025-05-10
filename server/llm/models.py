# utils/models.py

from typing import Any, Dict, Tuple
from llm.utils.prompt import InstructionConfig
from llm.utils.chatbot import ChatBot
from llm.utils.chain import LLMChain

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
                {"query": "서울 날씨 알려줘", "purpose_check": "no"},
                {"query": "부모님이랑 다음주 유럽 배낭여행 일정 알려줘", "purpose_check": "yes"},
                {"query": "AI 모델 구조 설명해줘", "purpose_check": "no"}
            ]
        )

        # 2) ChatBot 생성: 시스템 메시지는 상담 여부 판단 전문가로 설정
        self.chatbot = ChatBot(
            system_instruction="당신은 여행 경로 추천 요청을 판단하는 전문가입니다. 사용자의 요청이 여행이나 놀만한 장소, 갈만한 장소, 음식점 등을 추천받기를 요청하는지 판단해야합니다."
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
                "주어진 여행 요청 문장 다음 **입력: {query}** 에서 핵심 정보를 추출하여, '누구와', '어디를', '언제'를 포함한 문장으로 정제하세요."
            ),
            input_variables=["query"],
            examples=[
                {
                    "query": "친구와 다음 달 제주도 3박4일 여행 코스 추천해줘",
                    "refined_travel_prompt": "친구와 다음 달 제주도에서 3박4일 동안 여행 코스를 추천해 주세요."
                },
                {
                    "query": "서울에서 맛집 추천해줘",
                    "refined_travel_prompt": "서울에서 맛집을 추천해 주세요."
                },
                {
                    "query": "다음 달 여행 계획 짜줘",
                    "refined_travel_prompt": {
                        "companions": None,
                        "location": None,
                        "dates": "다음 달",
                        "tags": ["여행"],
                        "summary": "다음 달에 여행 계획을 세우고 싶습니다."
                    }
                },
                {
                    "query": "가족과 제주도 맛집 추천",
                    "refined_travel_prompt": {
                        "companions": "가족과",
                        "location": "제주도",
                        "dates": None,
                        "tags": ["맛집", "제주도", "가족"],
                        "summary": "가족과 제주도에서 맛집을 추천받고 싶습니다."
                    }
                }
            ]
        )

        refine_chatbot = ChatBot(system_instruction="여행 요청에서 동반자(companions), 장소(location), 일정(dates), 태그(tags), 요약(summary)를 JSON 형태로 반드시 반환하세요.")

        refine_chain = LLMChain(
            chatbot=refine_chatbot,
            prompt=refine_prompt_config,
            output_key="refined_travel_prompt"
        )

        result = refine_chain.run({"query": text})
        return result.get("refined_travel_prompt", "").strip()