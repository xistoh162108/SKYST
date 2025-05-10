import os
import requests
import base64
from dotenv import load_dotenv

# .env 로드 (경로 주의)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_tags_from_gemini(image_file) -> list:
    mime_type = image_file.mimetype  # ex: "image/jpeg"
    encoded = base64.b64encode(image_file.read()).decode("utf-8")
    image_data_url = f"data:{mime_type};base64,{encoded}"

    prompt = (
        "이 사진을 보고 장소, 분위기, 음식 관련 태그를 한글로 3~5개 추천해줘. "
        "예: ['카페', '데이트', '야경', '조명좋음'] 형식으로, 다른 텍스트 없이 리스트만."
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
                            "mimeType": mime_type,
                            "data": encoded
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

    print(response)

    try:
        raw_text = response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        return eval(raw_text) if raw_text.startswith("[") else [raw_text]
    except Exception as e:
        print("태그 생성 실패:", e)
        return []
