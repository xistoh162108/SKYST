from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage
from langchain_experimental.autonomous_agents.agentic import InstructionConfig, ChatBot


class InputChecker:
    """
    InputChecker adapted for travel route recommendation requests.
    Determines if a user's input is related to travel route recommendations,
    and refines the prompt to extract key travel information such as
    'who', 'where', and 'when'.
    """
    def __init__(self):
        examples = [
            {"query": "친구와 다음 달 제주도 3박4일 여행 코스 추천해줘", "purpose_check": "yes"},
            {"query": "서울 날씨 알려줘", "purpose_check": "no"}
        ]
        config = InstructionConfig(
            instruction="사용자의 다음 질문이 여행 경로 추천 요청과 관련된지 판단하세요. 관련 있으면 'yes', 아니면 'no'라고 답해주세요.\n\n여행 계획: {query}",
            input_variables=["query"],
            output_key="purpose_check",
            examples=examples
        )
        self.chain = LLMChain(
            llm=ChatOpenAI(model="gpt-4", temperature=0),
            prompt=config.to_prompt(),
            output_key=config.output_key,
        )

    def refine_prompt(self, text: str) -> str:
        refine_config = InstructionConfig(
            instruction="주어진 여행 요청 문장에서 핵심 정보를 추출하여, '누구와', '어디를', '언제'를 포함한 문장으로 정제하세요.\n\n원본 요청: {query}",
            input_variables=["query"],
            output_key="refined_travel_prompt"
        )
        refine_bot = ChatBot(
            system_instruction=SystemMessage(content="Prompt Refiner"),
            llm_chain=LLMChain(
                llm=ChatOpenAI(model="gpt-4", temperature=0),
                prompt=refine_config.to_prompt(),
                output_key=refine_config.output_key,
            )
        )
        result = refine_bot.llm_chain.run({"query": text})
        return result

    def is_travel_request(self, text: str) -> (bool, str):
        result = self.chain.run({"query": text})
        if result.lower() == "yes":
            refined = self.refine_prompt(text)
            return True, refined
        else:
            return False, None


            hello