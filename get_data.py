import requests
import os
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
from urllib.parse import unquote

load_dotenv()

def fetch_and_save_welfare_data():
    url = 'https://apis.data.go.kr/B554287/LocalGovernmentWelfareInformations/LcgvWelfarelist'
    service_key = os.environ.get("DATA_GO_KEY")

    if not service_key:
        print(" .env 파일 확인 필요")
        return

    # 1. 한 번에 1000개 요청 (최대치는 API마다 다르지만 보통 1000~2000 가능)
    params = {
        'serviceKey': unquote(service_key), 
        'pageNo': '1',
        'numOfRows': '1000', 
    }

    print("데이터 1000개를 요청 중입니다... (시간이 좀 걸릴 수 있어요)")
    response = requests.get(url, params=params)
    
    try:
        root = ET.fromstring(response.content)
        items = root.findall(".//servList")
        
        if not items:
            print("데이터 없음")
            return

        save_text = "[우리동네 노인 복지 정보 목록]\n(이 정보는 AI가 상담에 참고할 자료입니다)\n\n"
        count = 0
        
        # 2. 노인 관련 키워드 정의 (이 단어가 포함된 것만 저장)
        keywords = ["노인", "어르신", "65세", "치매", "독거", "중장년", "기초연금"]

        for item in items:
            title = item.findtext("servNm", "")
            target = item.findtext("lifeNmArray", "") # 생애주기 (청년, 노인 등)
            content = item.findtext("servDgst", "")
            link = item.findtext("servDtlLink", "#")
            
            # 검색할 전체 텍스트 (제목 + 대상 + 내용)
            full_text = f"{title} {target} {content}"

            # 3. 필터링: 키워드가 하나라도 들어있으면 저장
            if any(keyword in full_text for keyword in keywords):
                save_text += f"## {title}\n"
                save_text += f"- 대상: {target}\n"
                save_text += f"- 혜택: {content}\n"
                save_text += f"- 링크: {link}\n\n"
                count += 1

        with open("welfare_data.txt", "w", encoding="utf-8") as f:
            f.write(save_text)
        
        print(f" 전체 1000개 중 '노인' 관련 혜택 {count}개를 찾아 저장했습니다!")

    except Exception as e:
        print(f"에러 발생: {e}")

if __name__ == "__main__":
    fetch_and_save_welfare_data()