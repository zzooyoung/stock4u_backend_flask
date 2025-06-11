import requests
import logging
import pymysql
import json
import os
from dotenv import load_dotenv
from datetime import datetime
from config import TICKERS  # 리스트 형태: ["AMZN", "TSLA", ...]

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO)

# DB 설정
db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "database": os.getenv("DB_NAME"),
    "password": os.getenv("DB_PASSWORD"),
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor
}

# DB 저장 함수
def save_to_db(ticker, predictions):
    pred_close = predictions[0]
    pred_high = predictions[1]
    pred_low = predictions[2]
    pred_open = predictions[3]
    pred_volume = int(predictions[4])
    refresh_time = datetime.now()

    try:
        conn = pymysql.connect(**db_config)
        with conn.cursor() as cursor:
            # 기존 ticker에 대한 데이터 삭제
            delete_sql = "DELETE FROM prediction WHERE ticker = %s"
            cursor.execute(delete_sql, (ticker,))

            # 새로운 데이터 삽입
            insert_sql = """
                INSERT INTO prediction (
                    after_price, atOpen_price, higher_price, lower_price,
                    volumn, ticker, name, refresh_date
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_sql, (
                pred_close,
                pred_open,
                pred_high,
                pred_low,
                pred_volume,
                ticker,
                ticker,
                refresh_time
            ))
            conn.commit()
        conn.close()
        logging.info(f"✅ {ticker} 예측 결과 저장 완료.")
    except Exception as e:
        logging.error(f"❌ DB 저장 실패 ({ticker}): {e}")


# 모든 티커에 대해 반복 실행
for ticker in TICKERS:
    ticker_lower = ticker.lower()
    url = f"http://chaeseungji.site:30394/v1/models/{ticker_lower}-predictor:predict"
    json_file_path = f"./input_data/{ticker}_input.json"
    headers = {
        "Host": f"{ticker_lower}-predictor-kubeflow-user-example-com.kubeflow.chaeseungji.site",
        "Content-Type": "application/json"
    }

    try:
        with open(json_file_path, 'r') as f:
            json_data = f.read()

        response = requests.post(url, data=json_data, headers=headers)
        response.raise_for_status()

        predictions = response.json()["predictions"][0]
        save_to_db(ticker, predictions)

    except Exception as e:
        logging.error(f"❌ {ticker} 예측 처리 실패: {e}")