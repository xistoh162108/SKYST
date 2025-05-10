from typing import Dict, Any, Optional, List
from tools.google_places_api import GooglePlacesAPI
from tools.google_search_api import GoogleSearchAPI
from tools.tool_list import TOOL_LIST
from tools.people_photo import (
    get_photos_by_person,
    get_people_in_photo,
    add_person_to_photo,
)
from tools.people import get_person_by_id, get_all_people
from tools.photos import search_photo_by_id
from llm.models import *
from tools.notes import AgentNotes, NoteType
import os

class Tools:
    def __init__(self, photo_people_repo, photo_repo, people_repo, enable_notes: bool = True):
        self.google_places_api = GooglePlacesAPI()
        self.google_search_api = GoogleSearchAPI()
        self.photo_people_repo = photo_people_repo
        self.photo_repo = photo_repo
        self.people_repo = people_repo
        self.api_key = os.getenv("GOOGLE_API_KEY", "")  # 환경변수 또는 다른 방식으로 API 키 주입
        self.input_checker   = inputChecker(self.api_key)
        self.query_maker     = queryMaker(self.api_key)
        self.filter_generator = filterGenerator(self.api_key)
        self.tot_maker       = TOTMaker(self.api_key, self)
        self.tot_executor    = TOTExecutor(self.api_key, self)
        self.text_summarizer = TextSummarizer(self.api_key)
        self.custom_llm      = CustomLLM(self.api_key)
        
        # 에이전트 노트 초기화
        self.enable_notes = enable_notes
        if self.enable_notes:
            self.notes = AgentNotes()
        
        self.tool_mapping = {
            "1": lambda person_id: get_photos_by_person(self.photo_people_repo, person_id),
            "2": lambda photo_id: get_people_in_photo(self.photo_people_repo, photo_id),
            "3": lambda photo_id, person_id: add_person_to_photo(self.photo_people_repo, photo_id, person_id),
            # "4": plan_route
            "5": self.google_places_api.search_text,
            "6": self.google_places_api.get_place_details,
            "7": self.google_places_api.search_nearby,
            "9": self.google_search_api.search,
            "10": self.google_search_api.get_total_results,
            "11": self.google_search_api.get_page_content,
            "16": lambda person_id: get_person_by_id(self.people_repo, person_id),
            "17": lambda: get_all_people(self.people_repo),
            "18": lambda photo_id: search_photo_by_id(self.photo_repo, photo_id),
            "19": self._log_model_response(self.input_checker.process_query, "input_checker"),
            "20": self._log_model_response(self.query_maker.process_query, "query_maker"),
            "21": self._log_model_response(self.filter_generator.process_query, "filter_generator"),
            "22": self._log_model_response(self.tot_maker.process_query, "tot_maker"),
            "23": self._log_tot_execution(self.tot_executor.execute_plan),
            "24": self._log_model_response(self.text_summarizer.summarize, "text_summarizer"),
            "25": self._log_model_response(self.custom_llm.generate_response, "custom_llm"),
            "26": self._log_model_response(self.custom_llm.generate_with_context, "custom_llm")
        }

    def _log_tool_execution(self, tool_id: str, inputs: Dict[str, Any], result: Any):
        """도구 실행 결과 기록"""
        if not self.enable_notes:
            return
            
        tool_info = self.get_tool_info(tool_id)
        tool_name = tool_info.get("name", "unknown") if tool_info else "unknown"
            
        self.notes.add_note(
            note_type=NoteType.TOOL_EXECUTION,
            content={
                "tool_id": tool_id,
                "tool_name": tool_name,
                "inputs": inputs,
                "result": result
            }
        )

    def _log_model_response(self, func, model_name: str):
        """모델 응답 기록을 위한 데코레이터 함수"""
        def wrapper(*args, **kwargs):
            # 원래 함수 실행
            result = func(*args, **kwargs)
            
            # 로깅이 활성화된 경우에만 기록
            if self.enable_notes:
                # 첫 번째 인자가 self인 경우 제외 (메서드 호출)
                if args and isinstance(args[0], str):
                    user_message = args[0]
                else:
                    user_message = kwargs.get("user_message", "Unknown input")
                
                self.notes.add_note(
                    note_type=NoteType.MODEL_RESPONSE,
                    content={
                        "model_name": model_name,
                        "input": user_message,
                        "response": result
                    }
                )
            
            return result
        return wrapper

    def _log_tot_execution(self, func):
        """TOT 실행 기록을 위한 데코레이터 함수"""
        def wrapper(plan, *args, **kwargs):
            # 원래 함수 실행
            result = func(plan, *args, **kwargs)
            
            # 로깅이 활성화된 경우에만 기록
            if self.enable_notes:
                self.notes.add_note(
                    note_type=NoteType.TOT_EXECUTION,
                    content={
                        "plan": plan,
                        "result": result
                    }
                )
            
            return result
        return wrapper

    def log_error(self, error_type: str, message: str, details: Dict[str, Any] = None):
        """에러 기록"""
        if not self.enable_notes:
            return
            
        self.notes.add_note(
            note_type=NoteType.ERROR,
            content={
                "error_type": error_type,
                "message": message,
                "details": details or {}
            }
        )

    def get_tool_info(self, tool_id: str) -> Optional[Dict[str, Any]]:
        return TOOL_LIST.get(tool_id)

    def execute_tool(self, tool_id: str, **kwargs) -> Any:
        """
        도구 실행 메서드
        
        Args:
            tool_id (str): 도구 ID
            **kwargs: 도구에 전달할 매개변수
            
        Returns:
            Any: 도구 실행 결과
        """
        try:
            if tool_id not in self.tool_mapping:
                raise ValueError(f"Unknown tool ID: {tool_id}")
            
            tool_info = self.get_tool_info(tool_id)
            if not tool_info:
                raise ValueError(f"No information found for tool ID: {tool_id}")
            
            required_inputs = {
                k: v for k, v in tool_info["inputs"].items() 
                if "Optional" not in v
            }
            missing_inputs = [k for k in required_inputs if k not in kwargs]
            if missing_inputs:
                raise ValueError(f"Missing required inputs for tool {tool_id}: {missing_inputs}")
            
            # 도구 실행
            result = self.tool_mapping[tool_id](**kwargs)
            
            # 도구 실행 결과 기록 (TOT 실행, 모델 응답 제외)
            if tool_id not in ["19", "20", "21", "22", "23", "24", "25", "26"]:
                self._log_tool_execution(tool_id, kwargs, result)
                
            return result
            
        except Exception as e:
            # 오류 기록
            self.log_error("ToolExecutionError", str(e), {
                "tool_id": tool_id,
                "inputs": kwargs
            })
            raise
    
    def get_tool_list(self) -> Dict[str, Any]:
        return TOOL_LIST
    
    def get_notes(self) -> AgentNotes:
        """노트 객체 반환"""
        if not self.enable_notes:
            raise ValueError("Notes are not enabled for this Tools instance")
        return self.notes
    
    def get_session_summary(self) -> Dict[str, Any]:
        """현재 세션 요약 정보 반환"""
        if not self.enable_notes:
            raise ValueError("Notes are not enabled for this Tools instance")
        return self.notes.get_session_summary()
    
    def export_notes(self, format: str = "json") -> str:
        """노트 내보내기"""
        if not self.enable_notes:
            raise ValueError("Notes are not enabled for this Tools instance")
        return self.notes.export_notes(format)