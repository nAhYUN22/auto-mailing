import sys
import os
import webbrowser
import pandas as pd
from compare.compare_adobe2020 import compare_and_update_Adobe2020
from compare.compare_bandizip import compare_and_update_Bandizip
from compare.compare_chrome import compare_and_update_Chrome
from compare.compare_edge import compare_and_update_Edge
from compare.compare_engine import compare_and_update_Engine
from compare.compare_firefox import compare_and_update_Firefox
from compare.compare_hancom import compare_and_update_hancom
from compare.compare_adobe import compare_and_update_adobe
from compare.compare_itunes import compare_and_update_iTunes
from compare.compare_signature import compare_and_update_Signature
from compare.compare_whale import compare_and_update_Whale

# 프로젝트 루트를 모듈 경로에 추가
root = os.path.dirname(__file__)
sys.path.append(root)


def main():
    # 1) 비교 함수로부터 DataFrame 수집
    df_hancom = compare_and_update_hancom()
    df_adobe = compare_and_update_adobe()
    df_adobe2020 = compare_and_update_Adobe2020()
    df_chrome = compare_and_update_Chrome()
    df_firefox = compare_and_update_Firefox()
    df_bandizip = compare_and_update_Bandizip()
    df_edge = compare_and_update_Edge()
    df_signature = compare_and_update_Signature()
    df_engine = compare_and_update_Engine()
    df_itunes = compare_and_update_iTunes()
    df_whale = compare_and_update_Whale()

    # 2) DataFrame 합치기
    df_all = pd.concat(
        [
            df_hancom,
            df_adobe,
            df_adobe2020,
            df_chrome,
            df_firefox,
            df_bandizip,
            df_edge,
            df_signature,
            df_engine,
            df_itunes,
            df_whale,
        ],
        ignore_index=True,
    )

    # 3) HTML 보고서 생성
    report_path = os.path.join(root, "patch_report.html")
    df_all.to_html(report_path, index=False, classes="patch-table")

    # 4) 브라우저로 자동 열기
    webbrowser.open(f"file://{os.path.abspath(report_path)}")


if __name__ == "__main__":
    main()
