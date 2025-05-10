import os
import requests
from dotenv import load_dotenv

# .env 파일 경로: 현재 파일 기준 ../.env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

# 환경변수에서 Gemini API 키 불러오기
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_tags_from_gemini(image_data_url: str) -> list:
    prompt = (
        "이 사진을 보고 어울리는 장소나 분위기, 음식 관련 한글 태그를 3~5개 추출해줘. "
        "예: ['카페', '데이트', '야경', '조명좋음', '혼밥'] 형식. 리스트 외 텍스트는 주지 마."
    )

    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "contents": [
            {
                "parts": [
                    { "text": prompt },
                    {
                        "inlineData": {
                            "mimeType": "image/jpeg",
                            "data": image_data_url.split(",")[1]  # base64 부분만 추출
                        }
                    }
                ]
            }
        ]
    }

    response = requests.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent",
        headers=headers,
        params={"key": GEMINI_API_KEY},
        json=payload
    )

    result = response.json()
    try:
        raw_text = result["candidates"][0]["content"]["parts"][0]["text"].strip()
        return eval(raw_text) if raw_text.startswith("[") else [raw_text]
    except:
        return []
