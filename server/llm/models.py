import os
import sys
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from tools.tools import Tools

# 프로젝트 루트 디렉토리를 파이썬 경로에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Google Gemini API 임포트
import google.generativeai as genai

# 프롬프트 템플릿과 출력 파서 임포트
from llm.utils.prompt import InstructionConfig
from llm.utils.output_parsers import JSONOutputParser
from llm.utils.chatbot import ChatBot

class inputChecker:
    def __init__(self, api_key: str):
        """

        Args:
            api_key (str): Google API 키
        """
        self.api_key = api_key
        genai.configure(api_key=self.api_key)

        # JSON 출력 파서 생성
        self.json_parser = JSONOutputParser()

        # 시스템 프롬프트 설정
        self.checker_config = InstructionConfig(
                        instruction="""당신은 사용자의 요청을 받아 필터를 생성하고, DB에서 사진을 검색하고, 사용자에게 적절한 여행
                        코스를 추천해주는 챗봇의 입력을 검사하는 챗봇입니다. 
                        사용자의 입력이 챗봇의 목적에 부합하는지 검사하고 결과를 반환해야합니다.
                        사용자의 입력은 다음 목적들 혹은 유사 목적, 도메잊 중 하나이어야 합니다.
                        - 장소 추천
                        - 음식 추천
                        - 여행 코스 추천
                        - 액티비티 추천
                        - 카페 추천
                        - 여행 지역 추천
                        - 기타 유사 도메인
                        해당 내용을 바탕으로 사용자의 요청을 검사하고 JSON 형식으로 결과를 반환해야 합니다. 
            """,
            output_parser=self.json_parser,
            output_format={
                "is_valid": "사용자의 입력이 본 챗봇의 목적에 맞는지 여부 (true/false)",
            },
            examples=[
                {
                    "input": "지민이랑 내일 놀만한거 추천해줘.",
                    "output": {"is_valid": "true"}  # "output" 키 추가
                },
                {
                    "input": "인공지능이 뭐야",
                    "output": {"is_valid": "false"} # "output" 키 추가
                },
                {
                    "input": "대전에서 친구들이랑 놀건데 무엇을 먹는것이 좋을까? 카페도 추천해주면 좋겠어",
                    "output": {"is_valid": "true"}  # "output" 키 추가
                },
                {
                    "input": "서울 날씨 알려줘",
                    "output": {"is_valid": "false"} # "output" 키 추가
                },
                {
                    "input": "부모님이랑 다음주 유럽 배낭여행 일정 알려줘",
                    "output": {"is_valid": "true"}  # "output" 키 추가
                },
                {
                    "input": "나는 지금 너무 힘들어.",
                    "output": {"is_valid": "false"} # "output" 키 추가
                },
                {
                    "input": "안녕?",
                    "output": {"is_valid": "true"}  # "output" 키 추가
                }
                ]
        )

        self.checker = ChatBot(
                    model_name="gemini-2.0-flash",
                    temperature=0.5,  # 일관된 응답을 위해 낮은 온도 설정
                    max_output_tokens=1024,
                    instruction_config=self.checker_config,
                    api_key=self.api_key
                )

    def process_query(self, user_message: str) -> Dict[str, Any]:
        """
        사용자 쿼리 처리

        Args:
            user_message (str): 사용자 메시지

        Returns:
            Dict[str, Any]: 상담 응답
        """
        # 챗봇이 실행 중이 아니면 시작
        if not self.checker.is_running():
            self.checker.start_chat()

        # 사용자 메시지 처리
        response = self.checker.send_message(user_message)

        # 응답이 딕셔너리가 아니면 변환
        if not isinstance(response, dict):
            try:
                response = json.loads(response)
            except:
                return {
                    "is_valid": False,
                    "reason": "응답 형식 오류",
                    "message": "죄송합니다. 응답 처리 중 오류가 발생했습니다."
                }

        return response


class queryMaker:
    def __init__(self, api_key: str):
        """
        쿼리메이커

        Args:
            api_key (str): Google API 키
        """
        self.api_key = api_key
        genai.configure(api_key=self.api_key)

        # JSON 출력 파서 생성
        self.json_parser = JSONOutputParser()

        # 쿼리 제작자
        self.query_maker_config = InstructionConfig(
                        instruction="""당신은 회상의 검색을 하기 위해 고용된 검색 엔진 입력가입니다. 요청에 대해 최대한 다양한 측면에서 정보를 얻을 수 있도록 검색 쿼리를 생성해주세요.
                        """,
                        output_parser=self.json_parser,
                        output_format={
                            "queries":''# 타입 힌트 대신 빈 리스트 사용
                        },
                        examples=[
            {
                "input": "내일 서울 놀만한거.",
                "output": {
                "queries": [
                    "서울 여행 추천",
                    "서울 카페 추천",
                    "서울 공방 추천",
                    "서울 액티비티 추천",
                    "서울 맛집 추천"
                ]
                }
            },
            {
                "input": "부산 해운대에서 새벽 해돋이 볼 만한 곳 알려줘.",
                "output": {
                    "queries": [
                        "해운대 일출 명소",
                        "부산 새벽 바다 전망 좋은 장소",
                        "해운대 해돋이 추천 스팟"
                    ]
                }
            },
            {
                "input": "대전에서 부모님 모시고 산책할 공원 추천해줘.",
                "output": {
                    "queries": [
                        "대전 가족 산책 공원",
                        "대전 경치 좋은 공원",
                        "대전 부모님과 갈 만한 산책 코스",
                        "대전 한적한 산책길"
                    ]
                }
            },
            {
                "input": "제주도에 비 오는 날 실내 액티비티 뭐가 좋아?",
                "output": {
                    "queries": [
                        "제주도 실내 관광지",
                        "제주도 비 오는 날 가볼 곳",
                        "제주도 실내 체험 추천",
                        "제주도 실내 액티비티",
                        "제주도 비 오는 날 데이트 코스",
                        "제주도 비상시 관광"
                    ]
                }
            },
            {
                "input": "서울 근교 1박 2일 여행 코스 짜줘.",
                "output": {
                    "queries": [
                        "서울 근교 1박2일 추천",
                        "서울 근교 당일치기 여행지",
                        "서울 근교 캠핑장",
                        "서울 근교 숙소 추천"
                    ]
                }
            },
            {
                "input": "가을 단풍 명소 알려줄래?",
                "output": {
                    "queries": [
                        "가을 단풍 여행지",
                        "국내 단풍 절정 시기",
                        "서울 단풍 구경",
                        "가을 산행 추천 명산",
                        "단풍 사진 스팟"
                    ]
                }
            },
            {
                "input": "강릉 커피 거리에서 유명한 카페 추천해줘.",
                "output": {
                    "queries": [
                        "강릉 커피거리 카페",
                        "강릉 테라로사 외 카페",
                        "강릉 바다 보이는 카페"
                    ]
                }
            },
            {
                "input": "춘천에서 닭갈비 말고 색다른 음식 먹을 곳 있어?",
                "output": {
                    "queries": [
                        "춘천 닭갈비 대안 맛집",
                        "춘천 숨은 맛집",
                        "춘천 현지인 추천 음식",
                        "춘천 이색 음식점",
                        "춘천 맛집 리스트"
                    ]
                }
            },
            {
                "input": "여름 휴가로 제주 펜션 찾고 있어.",
                "output": {
                    "queries": [
                        "제주 펜션 추천",
                        "제주 수영장 있는 펜션",
                        "제주 오션뷰 숙소",
                        "제주 가족형 펜션",
                        "제주 애견동반 숙소",
                        "제주 성수기 숙소 예약"
                    ]
                }
            },
            {
                "input": "인천공항 근처 맛집 알려줘.",
                "output": {
                    "queries": [
                        "인천공항 근처 식당",
                        "영종도 맛집 추천",
                        "인천공항 근처 회식 장소"
                    ]
                }
            },
            {
                "input": "친구들이랑 서울 야경 예쁜 곳 어디가 좋아?",
                "output": {
                    "queries": [
                        "서울 야경 명소",
                        "서울 야경 드라이브 코스",
                        "서울 노을 전망대",
                        "서울 야경 카페",
                        "서울 야경 사진 스팟"
                    ]
                }
            }
            ]
        )   

        self.query_maker = ChatBot(
                    model_name="gemini-2.0-flash",
                    temperature=1.5,  # 일관된 응답을 위해 낮은 온도 설정
                    max_output_tokens=1024,
                    instruction_config=self.query_maker_config,
                    api_key=self.api_key
                )

    def process_query(self, user_message: str) -> Dict[str, Any]:
        """
        사용자 쿼리 처리

        Args:
            user_message (str): 사용자 메시지

        Returnsㅣ
            Dict[str, Any]: 응답
        """
        # 챗봇이 실행 중이 아니면 시작
        if not self.query_maker.is_running():
            self.query_maker.start_chat()

        # 사용자 메시지 처리
        response = self.query_maker.send_message(user_message)

        # 응답이 딕셔너리가 아니면 변환
        if not isinstance(response, dict):
            try:
                response = json.loads(response)
            except:
                return {
                    "is_valid": False,
                    "reason": "응답 형식 오류",
                    "message": "죄송합니다. 응답 처리 중 오류가 발생했습니다."
                }

        return response
    
class filterGenerator:
    def __init__(self, api_key: str):
        """
        필터 생성자 챗봇 초기화

        Args:
            api_key (str): Google API 키
        """
        self.api_key = api_key
        genai.configure(api_key=self.api_key)

        # JSON 출력 파서 생성
        self.json_parser = JSONOutputParser()

        # 오늘 날짜 가져오기
        today = datetime.now().strftime("%Y-%m-%d")

        # 필터 생성자 시스템 프롬프트 설정
        self.filter_generator_config = InstructionConfig(
            instruction=f"""오늘 날짜는 {today}입니다. 당신은 KAIST(한국과학기술원) 전산학부 챗봇 파이프라인의 일부로, 사용자의 질문을 분석하여 정보 검색을 위한 필터를 생성하는 역할을 수행합니다.

당신의 목표는 사용자의 질문에서 검색 결과를 좁힐 수 있는 최대 3개의 필터 단어만을 추출하는 것입니다.

- 필터 단어는 사용자의 질문에서 중요한 키워드를 기반으로 추출하며, 최대 3개까지 추출할 수 있습니다.

JSON 형식으로 응답하세요.
""",
            output_parser=self.json_parser,
            output_format={
                "filter_words": ["필터 단어 1", "필터 단어 2", "필터 단어 3"]
            },
            examples=[
                {
                    "input": "부산 해운대에서 새벽 해돋이 볼 만한 곳 알려줘.",
                    "output": {"filter_words": ["해운대", "일출", "명소"]}
                },
                {
                    "input": "대전에서 부모님 모시고 산책할 공원 추천해줘.",
                    "output": {"filter_words": ["대전", "공원", "산책"]}
                },
                {
                    "input": "제주도에 비 오는 날 실내 액티비티 뭐가 좋아?",
                    "output": {"filter_words": ["제주도", "실내", "액티비티"]}
                },
                {
                    "input": "서울 근교 1박 2일 여행 코스 짜줘.",
                    "output": {"filter_words": ["서울 근교", "1박 2일", "여행"]}
                },
                {
                    "input": "가을 단풍 명소 알려줄래?",
                    "output": {"filter_words": ["가을", "단풍", "명소"]}
                },
                {
                    "input": "친구들이랑 서울 야경 예쁜 곳 어디가 좋아?",
                    "output": {"filter_words": ["서울", "야경", "예쁜 곳"]}
                }
            ]
        )

        self.filter_generator = ChatBot(
            model_name="gemini-2.0-flash",
            temperature=0.5,  # 일관된 응답을 위해 낮은 온도 설정
            max_output_tokens=1024,
            instruction_config=self.filter_generator_config,
            api_key=self.api_key
        )

    def process_query(self, user_message: str) -> Dict[str, Optional[Any]]:
        """
        사용자 쿼리를 처리하여 필터 정보를 추출합니다.

        Args:
            user_message (str): 사용자 메시지

        Returns:
            Dict[str, Optional[Any]]: 추출된 필터 정보 (시작 날짜, 끝 날짜, 필터 단어 리스트)
        """
        # 챗봇이 실행 중이 아니면 시작
        if not self.filter_generator.is_running():
            self.filter_generator.start_chat()

        # 사용자 메시지 처리
        response = self.filter_generator.send_message(user_message)

        # 응답이 딕셔너리가 아니면 변환
        if not isinstance(response, dict):
            try:
                response = json.loads(response)
            except:
                return {
                    "start_date": None,
                    "end_date": None,
                    "filter_words":'',
                    "reason": "응답 형식 오류",
                    "message": "죄송합니다. 응답 처리 중 오류가 발생했습니다."
                }

        return response

class TOTMaker:
    def __init__(self, api_key: str, tools: Tools):
        """
        TOT 메이커 초기화

        Args:
            api_key (str): Google API 키
            tools (Tools): 도구 인스턴스 (도구 목록 조회용)
        """
        self.api_key = api_key
        self.tools = tools
        genai.configure(api_key=self.api_key)

        # JSON 출력 파서 생성
        self.json_parser = JSONOutputParser()

        # TOT 메이커 시스템 프롬프트 설정
        self.tot_maker_config = InstructionConfig(
            instruction="""당신은 사용자의 요청을 달성하기 위한 실행 계획을 수립하는 TOT(Tree of Thoughts) 메이커입니다.
            주어진 도구 목록을 분석하고, 사용자의 요청을 달성하기 위해 필요한 도구들을 순서대로 실행하는 계획을 생성해야 합니다.

            각 단계는 다음 정보를 포함해야 합니다:
            - step_id: 단계 번호
            - tool_id: 사용할 도구의 ID
            - tool_name: 도구의 이름
            - description: 이 단계에서 수행할 작업 설명
            - inputs: 도구에 전달할 입력 파라미터
            - expected_output: 예상되는 출력 결과

            JSON 형식으로 응답하세요.
            """,
            output_parser=self.json_parser,
            output_format={
                "steps": [
                    {
                        "step_id": "int — 단계 번호",
                        "tool_id": "str — 사용할 도구 ID",
                        "tool_name": "str — 도구 이름",
                        "description": "str — 수행할 작업 설명",
                        "inputs": "Dict — 도구 입력 파라미터",
                        "expected_output": "str — 예상 출력 설명"
                    }
                ]
            },
            examples=[
                {
                    "input": "서울에서 맛있는 카페 추천해줘",
                    "output": {
                        "steps": [
                            {
                                "step_id": 1,
                                "tool_id": "5",
                                "tool_name": "gp_search_text",
                                "description": "서울의 카페를 검색합니다",
                                "inputs": {
                                    "text_query": "서울 맛있는 카페",
                                    "page_size": 5
                                },
                                "expected_output": "검색된 카페 목록"
                            },
                            {
                                "step_id": 2,
                                "tool_id": "6",
                                "tool_name": "gp_get_place_details",
                                "description": "첫 번째 카페의 상세 정보를 조회합니다",
                                "inputs": {
                                    "place_id": "검색 결과의 첫 번째 place_id"
                                },
                                "expected_output": "카페의 상세 정보"
                            }
                        ]
                    }
                }
            ]
        )

        self.tot_maker = ChatBot(
            model_name="gemini-2.0-flash",
            temperature=0.5,
            max_output_tokens=1024,
            instruction_config=self.tot_maker_config,
            api_key=self.api_key
        )

    def process_query(self, user_message: str) -> Dict[str, Any]:
        """
        사용자 쿼리를 처리하여 실행 계획을 생성합니다.

        Args:
            user_message (str): 사용자 메시지

        Returns:
            Dict[str, Any]: 생성된 실행 계획
        """
        # 챗봇이 실행 중이 아니면 시작
        if not self.tot_maker.is_running():
            self.tot_maker.start_chat()

        # 도구 목록 가져오기
        tool_list = self.tools.get_tool_list()
        
        # 도구 목록을 문자열로 변환
        tool_info = "사용 가능한 도구 목록:\n"
        for tool_id, tool in tool_list.items():
            tool_info += f"\n도구 ID: {tool_id}\n"
            tool_info += f"이름: {tool['name']}\n"
            tool_info += f"설명: {tool['description']}\n"
            tool_info += f"입력: {tool['inputs']}\n"
            tool_info += f"출력: {tool['outputs']}\n"
            tool_info += "---\n"

        # 사용자 메시지와 도구 목록을 함께 전달
        full_message = f"{tool_info}\n\n사용자 요청: {user_message}"
        
        # 사용자 메시지 처리
        response = self.tot_maker.send_message(full_message)

        # 응답이 딕셔너리가 아니면 변환
        if not isinstance(response, dict):
            try:
                response = json.loads(response)
            except:
                return {
                    "error": "응답 형식 오류",
                    "message": "죄송합니다. 응답 처리 중 오류가 발생했습니다."
                }

        return response

class TOTExecutor:
    def __init__(self, api_key: str, tools: Tools):
        """
        TOT 실행기 초기화

        Args:
            api_key (str): Google API 키
            tools (Tools): 도구 인스턴스
        """
        self.api_key = api_key
        self.tools = tools
        genai.configure(api_key=self.api_key)

        # JSON 출력 파서 생성
        self.json_parser = JSONOutputParser()

        # TOT 실행기 시스템 프롬프트 설정
        self.tot_executor_config = InstructionConfig(
            instruction="""당신은 TOT(Tree of Thoughts) 실행 계획을 단계별로 실행하고 분석하는 실행기입니다.
            각 단계를 실행하고, 결과를 분석하여 다음 단계로 넘어갈지 결정해야 합니다.

            각 단계 실행 후 다음을 수행해야 합니다:
            1. 실행 결과 분석
            2. 결과가 충분한지 판단
            3. 부족하다면 다른 방법으로 재시도 (최대 3번)
            4. 다음 단계로 넘어갈 준비

            JSON 형식으로 응답하세요.
            """,
            output_parser=self.json_parser,
            output_format={
                "analysis": {
                    "is_sufficient": "bool — 결과가 충분한지 여부",
                    "reason": "str — 판단 이유",
                    "retry_count": "int — 재시도 횟수",
                    "next_action": "str — 다음 행동 (continue/retry/stop)"
                },
                "summary": "str — 현재까지의 실행 결과 요약",
                "next_step_input": "Dict — 다음 단계에 전달할 입력값"
            }
        )

        self.tot_executor = ChatBot(
            model_name="gemini-2.0-flash",
            temperature=0.5,
            max_output_tokens=1024,
            instruction_config=self.tot_executor_config,
            api_key=self.api_key
        )

    def execute_step(self, step: Dict[str, Any], previous_results: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        단일 단계를 실행하고 결과를 분석합니다.

        Args:
            step (Dict[str, Any]): 실행할 단계 정보
            previous_results (List[Dict[str, Any]], optional): 이전 단계들의 결과

        Returns:
            Dict[str, Any]: 실행 결과와 분석
        """
        if not self.tot_executor.is_running():
            self.tot_executor.start_chat()

        # 이전 결과 요약 생성
        previous_summary = ""
        if previous_results:
            previous_summary = "이전 단계 결과:\n"
            for idx, result in enumerate(previous_results, 1):
                previous_summary += f"단계 {idx}: {result.get('summary', '')}\n"

        # 현재 단계 실행
        try:
            result = self.tools.execute_tool(tool_id=step['tool_id'], **step['inputs'])
        except Exception as e:
            return {
                "error": str(e),
                "analysis": {
                    "is_sufficient": False,
                    "reason": f"도구 실행 중 오류 발생: {str(e)}",
                    "retry_count": 0,
                    "next_action": "stop"
                },
                "summary": f"오류 발생: {str(e)}",
                "next_step_input": None
            }

        # 실행 결과 분석을 위한 프롬프트 생성
        analysis_prompt = f"""
        {previous_summary}
        
        현재 단계 정보:
        - 단계 ID: {step['step_id']}
        - 도구: {step['tool_name']}
        - 설명: {step['description']}
        - 예상 출력: {step['expected_output']}
        
        실행 결과:
        {json.dumps(result, ensure_ascii=False, indent=2)}
        
        위 정보를 바탕으로 다음을 분석해주세요:
        1. 결과가 충분한지
        2. 부족하다면 어떤 정보가 더 필요한지
        3. 다음 단계로 넘어갈 준비가 되었는지
        """

        # 결과 분석
        try:
            analysis = self.tot_executor.send_message(analysis_prompt)
            
            # analysis가 문자열인 경우 JSON으로 파싱 시도
            if isinstance(analysis, str):
                try:
                    analysis = json.loads(analysis)
                except json.JSONDecodeError:
                    # JSON 파싱 실패 시 기본값 설정
                    analysis = {
                        "is_sufficient": True,
                        "reason": "응답 파싱 실패",
                        "retry_count": 0,
                        "next_action": "continue"
                    }
            
            # 필수 키가 없는 경우 기본값 설정
            if not isinstance(analysis, dict):
                analysis = {
                    "is_sufficient": True,
                    "reason": "응답 형식 오류",
                    "retry_count": 0,
                    "next_action": "continue"
                }
            
            # 필수 키가 없는 경우 기본값으로 채우기
            analysis.setdefault("is_sufficient", True)
            analysis.setdefault("reason", "응답 분석 완료")
            analysis.setdefault("retry_count", 0)
            analysis.setdefault("next_action", "continue")
            
            return {
                "result": result,
                "analysis": analysis,
                "summary": analysis.get("summary", "분석 완료"),
                "next_step_input": analysis.get("next_step_input", {})
            }
        except Exception as e:
            return {
                "error": str(e),
                "analysis": {
                    "is_sufficient": False,
                    "reason": f"분석 중 오류 발생: {str(e)}",
                    "retry_count": 0,
                    "next_action": "stop"
                },
                "summary": f"오류 발생: {str(e)}",
                "next_step_input": None
            }

    def execute_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        전체 실행 계획을 순차적으로 실행합니다.

        Args:
            plan (Dict[str, Any]): 실행 계획

        Returns:
            Dict[str, Any]: 전체 실행 결과
        """
        results = []
        current_step = 0
        max_retries = 3

        while current_step < len(plan['steps']):
            step = plan['steps'][current_step]
            retry_count = 0
            step_result = None

            while retry_count < max_retries:
                # 단계 실행
                step_result = self.execute_step(step, results)
                
                # 결과 분석
                if step_result.get('error'):
                    return {
                        "steps": results,  # 여기에 steps 키 추가
                        "error": step_result['error'],
                        "final_summary": f"오류 발생: {step_result['error']}"
                    }

                analysis = step_result['analysis']
                
                # 충분한 결과를 얻었거나 최대 재시도 횟수에 도달한 경우
                if analysis['is_sufficient'] or retry_count >= max_retries - 1:
                    break

                # 재시도
                retry_count += 1
                step['inputs'] = step_result['next_step_input']

            # 결과 저장
            results.append(step_result)
            
            # 다음 단계로 진행
            if analysis['next_action'] == 'continue':
                current_step += 1
            elif analysis['next_action'] == 'stop':
                break

        return {
            "steps": results,  # 여기에 steps 키 추가
            "final_summary": "\n".join([r['summary'] for r in results])
        }