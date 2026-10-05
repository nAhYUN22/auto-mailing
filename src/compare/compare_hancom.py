import sys
import os
import json
import pandas as pd
from scrapers.hancom import HancomCrawler

# 프로젝트 루트를 모듈 경로에 추가
sys.path.append(os.path.dirname(__file__))

# last_version.json 경로
JSON_PATH = os.path.join(os.path.dirname(__file__), "last_version.json")


def compare_and_update_hancom() -> pd.DataFrame:
    """
    한컴오피스 패치 비교 후 DataFrame 반환
    """
    # 1) 이전 버전 로드
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            last_seen = json.load(f)
    except FileNotFoundError:
        last_seen = {}

    # 2) 크롤러 실행
    crawler = HancomCrawler()
    new_data = crawler._get_latest_update()  # {'HNC2024': ['날짜','버전'], ...}
    crawler.close()

    # 3) 비교 및 JSON 갱신
    rows = []
    for key, (patch_date, new_version) in new_data.items():
        old_version = last_seen.get(key, "")
        status = "❌" if old_version != new_version else "🟢"
        last_seen[key] = new_version
        rows.append(
            {
                "Product": key,
                "Last Update": patch_date,
                "Old Version": old_version,
                "New Version": new_version,
                "Status": status,
            }
        )

    # 4) JSON 저장
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(last_seen, f, ensure_ascii=False, indent=2)

    # 5) DataFrame 생성
    df = pd.DataFrame(rows)
    # (선택) 제품 코드 대신 한글명 매핑
    df["Product"] = (
        df["Product"]
        .map(
            {
                "HNC2024": "한컴오피스 2024",
                "HNC2022": "한컴오피스 2022",
                "HNC2020": "한컴오피스 2020",
                "HNC2018": "한컴오피스 2018",
                "HNCNEO": "한컴오피스 NEO",
            }
        )
        .fillna(df["Product"])
    )
    return df
