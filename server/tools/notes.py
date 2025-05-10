import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum

class NoteType(Enum):
    """노트 타입 정의"""
    TOOL_EXECUTION = "tool_execution"  # 도구 실행 기록
    MODEL_RESPONSE = "model_response"  # 모델 응답 기록
    TOT_PLAN = "tot_plan"             # TOT 계획 기록
    TOT_EXECUTION = "tot_execution"   # TOT 실행 기록
    ERROR = "error"                   # 오류 기록
    SUMMARY = "summary"               # 요약 기록

class AgentNotes:
    def __init__(self, base_dir: str = "notes"):
        """
        에이전트 노트 초기화

        Args:
            base_dir (str): 노트 저장 기본 디렉토리
        """
        self.base_dir = base_dir
        self.current_session = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = os.path.join(base_dir, self.current_session)
        
        # 세션 디렉토리 생성
        os.makedirs(self.session_dir, exist_ok=True)
        
        # 노트 파일 경로
        self.notes_file = os.path.join(self.session_dir, "notes.json")
        self.initialize_notes()

    def initialize_notes(self):
        """노트 파일 초기화"""
        if not os.path.exists(self.notes_file):
            initial_data = {
                "session_id": self.current_session,
                "start_time": datetime.now().isoformat(),
                "notes": []
            }
            self._save_notes(initial_data)

    def _save_notes(self, data: Dict[str, Any]):
        """노트 저장"""
        with open(self.notes_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_notes(self) -> Dict[str, Any]:
        """노트 로드"""
        with open(self.notes_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def add_note(self, 
                 note_type: NoteType,
                 content: Dict[str, Any],
                 metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        새로운 노트 추가

        Args:
            note_type (NoteType): 노트 타입
            content (Dict[str, Any]): 노트 내용
            metadata (Dict[str, Any], optional): 추가 메타데이터

        Returns:
            str: 노트 ID
        """
        notes_data = self._load_notes()
        
        note_id = f"{note_type.value}_{len(notes_data['notes']) + 1}"
        timestamp = datetime.now().isoformat()
        
        note = {
            "id": note_id,
            "type": note_type.value,
            "timestamp": timestamp,
            "content": content,
            "metadata": metadata or {}
        }
        
        notes_data['notes'].append(note)
        self._save_notes(notes_data)
        
        return note_id

    def get_note(self, note_id: str) -> Optional[Dict[str, Any]]:
        """
        특정 노트 조회

        Args:
            note_id (str): 노트 ID

        Returns:
            Optional[Dict[str, Any]]: 노트 내용
        """
        notes_data = self._load_notes()
        for note in notes_data['notes']:
            if note['id'] == note_id:
                return note
        return None

    def get_notes_by_type(self, note_type: NoteType) -> List[Dict[str, Any]]:
        """
        특정 타입의 모든 노트 조회

        Args:
            note_type (NoteType): 노트 타입

        Returns:
            List[Dict[str, Any]]: 노트 목록
        """
        notes_data = self._load_notes()
        return [note for note in notes_data['notes'] 
                if note['type'] == note_type.value]

    def get_tool_execution_notes(self, tool_id: str) -> List[Dict[str, Any]]:
        """
        특정 도구의 실행 기록 조회

        Args:
            tool_id (str): 도구 ID

        Returns:
            List[Dict[str, Any]]: 도구 실행 기록
        """
        tool_notes = self.get_notes_by_type(NoteType.TOOL_EXECUTION)
        return [note for note in tool_notes 
                if note['content'].get('tool_id') == tool_id]

    def get_model_response_notes(self, model_name: str) -> List[Dict[str, Any]]:
        """
        특정 모델의 응답 기록 조회

        Args:
            model_name (str): 모델 이름

        Returns:
            List[Dict[str, Any]]: 모델 응답 기록
        """
        model_notes = self.get_notes_by_type(NoteType.MODEL_RESPONSE)
        return [note for note in model_notes 
                if note['content'].get('model_name') == model_name]

    def get_tot_plan_notes(self) -> List[Dict[str, Any]]:
        """
        TOT 계획 기록 조회

        Returns:
            List[Dict[str, Any]]: TOT 계획 기록
        """
        return self.get_notes_by_type(NoteType.TOT_PLAN)

    def get_tot_execution_notes(self) -> List[Dict[str, Any]]:
        """
        TOT 실행 기록 조회

        Returns:
            List[Dict[str, Any]]: TOT 실행 기록
        """
        return self.get_notes_by_type(NoteType.TOT_EXECUTION)

    def get_error_notes(self) -> List[Dict[str, Any]]:
        """
        오류 기록 조회

        Returns:
            List[Dict[str, Any]]: 오류 기록
        """
        return self.get_notes_by_type(NoteType.ERROR)

    def get_session_summary(self) -> Dict[str, Any]:
        """
        현재 세션의 요약 정보 조회

        Returns:
            Dict[str, Any]: 세션 요약
        """
        notes_data = self._load_notes()
        summary = {
            "session_id": notes_data["session_id"],
            "start_time": notes_data["start_time"],
            "end_time": datetime.now().isoformat(),
            "total_notes": len(notes_data["notes"]),
            "note_types": {},
            "tool_executions": {},
            "model_responses": {},
            "errors": []
        }

        for note in notes_data["notes"]:
            note_type = note["type"]
            summary["note_types"][note_type] = summary["note_types"].get(note_type, 0) + 1

            if note_type == NoteType.TOOL_EXECUTION.value:
                tool_id = note["content"].get("tool_id")
                if tool_id:
                    summary["tool_executions"][tool_id] = summary["tool_executions"].get(tool_id, 0) + 1

            elif note_type == NoteType.MODEL_RESPONSE.value:
                model_name = note["content"].get("model_name")
                if model_name:
                    summary["model_responses"][model_name] = summary["model_responses"].get(model_name, 0) + 1

            elif note_type == NoteType.ERROR.value:
                summary["errors"].append(note["content"])

        return summary

    def export_notes(self, format: str = "json") -> str:
        """
        노트 내보내기

        Args:
            format (str): 내보내기 형식 ("json" 또는 "txt")

        Returns:
            str: 내보낸 파일 경로
        """
        notes_data = self._load_notes()
        export_file = os.path.join(self.session_dir, f"export_{self.current_session}.{format}")
        
        if format == "json":
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(notes_data, f, ensure_ascii=False, indent=2)
        elif format == "txt":
            with open(export_file, 'w', encoding='utf-8') as f:
                f.write(f"Session ID: {notes_data['session_id']}\n")
                f.write(f"Start Time: {notes_data['start_time']}\n")
                f.write(f"Total Notes: {len(notes_data['notes'])}\n\n")
                
                for note in notes_data['notes']:
                    f.write(f"Note ID: {note['id']}\n")
                    f.write(f"Type: {note['type']}\n")
                    f.write(f"Timestamp: {note['timestamp']}\n")
                    f.write(f"Content: {json.dumps(note['content'], ensure_ascii=False, indent=2)}\n")
                    f.write(f"Metadata: {json.dumps(note['metadata'], ensure_ascii=False, indent=2)}\n")
                    f.write("-" * 80 + "\n")
        
        return export_file