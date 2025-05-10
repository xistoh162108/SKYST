from llm.models import InputChecker

def main():
    checker = InputChecker()

    # 1) Travel request true case
    text1 = "친구와 다음 달 제주도 3박4일 여행 코스 추천해줘"
    result1, prompt1 = checker.is_travel_request(text1)
    print(f"Input: {text1}")
    print(f"Is travel request? {result1}")
    print(f"Refined prompt: {prompt1}")
    print("-" * 40)

    # 2) Travel request false case
    text2 = "서울 날씨 알려줘"
    result2, prompt2 = checker.is_travel_request(text2)
    print(f"Input: {text2}")
    print(f"Is travel request? {result2}")
    print(f"Refined prompt: {prompt2}")
    print("-" * 40)

    # 3) Direct refine_prompt test
    text3 = "가족과 올 여름 부산 바다 여행 계획 알려줘"
    prompt3 = checker.refine_prompt(text3)
    print(f"Input: {text3}")
    print(f"Refined prompt: {prompt3}")

if __name__ == "__main__":
    main()