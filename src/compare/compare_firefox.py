import sys
import os
import json
import pandas as pd
from scrapers.firefox import FirefoxCrawler

# 프로젝트 루트를 모듈 경로에 추가
sys.path.append(os.path.dirname(__file__))

# last_version.json 경로
JSON_PATH = os.path.join(os.path.dirname(__file__), "last_version.json")


def compare_and_update_Firefox() -> pd.DataFrame:
    """
    Firefox 패치 비교 후 DataFrame 반환
    """
    # 1) 이전 버전 로드
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            last_seen = json.load(f)
    except FileNotFoundError:
        last_seen = {}

    # 2) 크롤러 실행
    crawler = FirefoxCrawler()
    date, version = crawler._get_latest_update()  # (날짜, 버전)
    crawler.close()

    # 3) 비교 및 JSON 갱신
    old_version = last_seen.get("Firefox", "")
    status = "❌" if old_version != version else "🟢"
    last_seen["Firefox"] = version
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(last_seen, f, ensure_ascii=False, indent=2)

    # 4) DataFrame 생성
    df = pd.DataFrame(
        [
            {
                "Product": "Firefox",
                "Last Update": date,
                "Old Version": old_version,
                "New Version": version,
                "Status": status,
            }
        ]
    )
    return df
