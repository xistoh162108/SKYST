from models import inputChecker, queryMaker, filterGenerator
import os
import json

def main():
    """
    inputChecker, queryMaker, FilterGenerator를 사용하는 메인 함수
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("GOOGLE_API_KEY 환경 변수가 설정되지 않았습니다.")
        return

    checker = inputChecker(api_key=api_key)
    maker = queryMaker(api_key=api_key)
    filter_generator = filterGenerator(api_key=api_key)

    while True:
        user_input = input("사용자 질문 (종료하려면 'exit' 입력): ")
        if user_input.lower() == 'exit':
            break

        # 입력 검사
        check_result = checker.process_query(user_input)
        print("\n입력 검사 결과:")
        print(json.dumps(check_result, indent=4, ensure_ascii=False))

        if check_result.get("is_valid"):
            # 쿼리 생성
            query_result = maker.process_query(user_input)
            print("\n쿼리 생성 결과:")
            print(json.dumps(query_result, indent=4, ensure_ascii=False))

            # 필터 생성
            filter_result = filter_generator.process_query(user_input)
            print("\n필터 생성 결과:")
            print(json.dumps(filter_result, indent=4, ensure_ascii=False))

        else:
            print("\n부적절한 입력으로 인해 쿼리 및 필터 생성을 중단합니다.")

if __name__ == "__main__":
    main()