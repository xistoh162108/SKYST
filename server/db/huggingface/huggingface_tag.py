import os
import requests
import base64
from dotenv import load_dotenv

# .env에서 HUGGINGFACE_API_KEY 로드
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
#api_key = os.getenv("HUGGINGFACE_API_KEY")
#print(f"API 키 확인: {api_key}")
def get_tags_from_huggingface(image_file) -> list:
    image_bytes = image_file.read()
    encoded = base64.b64encode(image_bytes).decode("utf-8")

    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "inputs": encoded
    }

    response = requests.post(
        url="https://api-inference.huggingface.co/models/google/vit-base-patch16-224",
        headers=headers,
        json=payload
    )

    try:
        result = response.json()
        return [x["label"] for x in sorted(result, key=lambda r: -r["score"])[:5]]
    except Exception as e:
        print("태그 추출 실패:", e)
        print("응답:", response.text)
        return []
