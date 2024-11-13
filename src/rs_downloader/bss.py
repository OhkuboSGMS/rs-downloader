import re
from datetime import datetime

from bs4 import BeautifulSoup


def extract_project(element: BeautifulSoup) -> dict:
    name = element.select_one(
        "span.MuiTypography-root.MuiTypography-headingXXSmall"
    ).get_text()
    # 日付とレコード数を取得
    info_text = element.select_one(
        "span.MuiTypography-root.MuiTypography-bodySmall"
    ).get_text()
    if " • " not in info_text:
        date, recordings = info_text, "0"
    else:
        date, recordings = info_text.split(" • ")
        match = re.search(r"\d+", recordings)
        if match:
            number = match.group()
            recordings = int(number)

    return {"name": name, "date": date, "recordings": recordings}


def extract_recording(element: BeautifulSoup):
    # タイトルを取得
    title_element = element.find(
        "span", {"data-automation-class": "recordings recording-title"}
    )
    title = title_element.text if title_element else "No title found"

    # レコードの日付を取得
    date_element = element.find(
        "span", {"data-automation-class": "recordings recording-date"}
    )
    record_date = date_element.text if date_element else "No date found"
    match = re.search(r"\b\w{3} \d{1,2}, \d{4} \d{1,2}:\d{2} (AM|PM)\b", record_date)
    # 日付が見つかった場合は返す、見つからなければ空文字を返す
    if match:
        date_str = match.group(0)
        # 日付文字列をdatetimeオブジェクトに変換
        record_date = datetime.strptime(date_str, "%b %d, %Y %I:%M %p")
    else:
        record_date = None
    # 結果を辞書で返す
    return {"title": title, "recorded_date": record_date}