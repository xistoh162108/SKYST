지금 구현해야하는 것들. 
<<<<<<< HEAD
=======

1. Tool로 검색하는것들 필요함. 
2. 필터링 기능? 
3. 사람이 있을 때 -> photo_people DB 사용. people id로 photo 전체 검색, 반환.
4.  

photo에 대해서는, photo_tags또는 photo 테이블 이용해서 정보 다 가져와야할듯. 
>>>>>>> feature/llm_agent

1. Tool로 검색하는것들 필요함. 
2. 필터링 기능? 
3. 사람이 있을 때 -> photo_people DB 사용. people id로 photo 전체 검색, 반환. 

<<<<<<< HEAD
photo에 대해서는, photo_tags또는 photo 테이블 이용해서 정보 다 가져와야할듯. 
=======
1. Input 검사
2. Input 정제
3. Input 바탕으로 작업을 결정.
   1. 예를 들어서, 누구와 어디를 간다. 
   2. 누구를 검색
   3. 어떤 태그가 나왔나 분석 -> 이 정보를 바탕으로 검색 쿼리를 설정. 
   4. 검색!
   5. 장소 비교, 판단
4. Input 경로를 추천해달라.
   1. 누구의 시간 타임라인을 비교. -> 타임라인에 대한 통계가 필요함. 

people_photo.py -> 사람을 기준으로 검색. 
photo.py -> 사진 ID를 기준으로 리스트업
>>>>>>> feature/llm_agent
