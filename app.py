from flask import Flask, request, jsonify
import pymysql
import os
from dotenv import load_dotenv
import requests
import logging
import json
from flask_cors import CORS


# .env 파일 로드
load_dotenv()

app = Flask(__name__)
CORS(app)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)



# 환경변수로부터 DB 설정 읽기
db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor
}

@app.route('/test', methods=['GET'])
def test():
    url = 'http://chaeseungji.site:30394/v1/models/nvda-predictor:predict'
    # JSON 파일을 불러와 데이터로 사용
    json_file_path = './nvda_input.json'
    try:
        with open(json_file_path, 'r') as f:
            json_data = f.read()

        # 요청 보내기
        headers = {
            'Host': 'nvda-predictor-kubeflow-user-example-com.kubeflow.chaeseungji.site',
            'Content-Type': 'application/json'
        }

        response = requests.post(url, data=json_data, headers=headers)

        # 응답 출력
        logging.info(f"Status Code: {response.status_code}")
        logging.info(f"Response Body: {response.json()}")

        

    except Exception as e:
        logging.error(f"Request failed: {e}")

@app.route('/users', methods=['GET'])
def get_users():
    try:
        conn = pymysql.connect(**db_config)
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
        conn.close()
        return jsonify(users)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/users', methods=['POST'])
def add_user():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')

    try:
        conn = pymysql.connect(**db_config)
        with conn.cursor() as cursor:
            sql = "INSERT INTO users (name, email) VALUES (%s, %s)"
            cursor.execute(sql, (name, email))
            conn.commit()
        conn.close()
        return jsonify({"message": "User added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stock-data', methods=['POST'])
def get_multiple_stock_data():
    try:
        data = request.get_json()
        tickers = data.get('tickers', [])

        if not tickers:
            return jsonify({"error": "No tickers provided"}), 400

        all_data = []

        for ticker in tickers:
            file_path = f"./input_data/{ticker}_input.json"
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    raw_data = json.load(f).get("instances", [[]])[0]

                    formatted = [
                        {
                            "symbol": ticker,
                            "open": row[0],
                            "high": row[1],
                            "low": row[2],
                            "close": row[3],
                            "volume": row[4],
                            "category": "tech"  # 임시 분류, 필요시 자동화 가능
                        }
                        for row in raw_data
                    ]

                    all_data.extend(formatted)
            else:
                return jsonify({"error": f"File not found for {ticker}"}), 404

        return jsonify(all_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/predict", methods=["POST"])
def get_predictions():
    data = request.get_json()
    tickers = data.get("tickers")

    if not tickers or not isinstance(tickers, list):
        return jsonify({"error": "tickers must be a list"}), 400

    predictions = []

    try:
        conn = pymysql.connect(**db_config)
        with conn.cursor() as cursor:
            for ticker in tickers:
                sql = """
                    SELECT after_price, higher_price, lower_price
                    FROM prediction
                    WHERE ticker = %s
                    ORDER BY refresh_date DESC
                    LIMIT 1
                """
                cursor.execute(sql, (ticker,))
                result = cursor.fetchone()

                if result:
                    predictions.append({
                        "symbol": ticker,
                        "predicted_close": result["after_price"],
                        "predicted_high": result["higher_price"],
                        "predicted_low": result["lower_price"]
                    })

        conn.close()
        return jsonify(predictions)

    except Exception as e:
        print(f"[ERROR] /predict 실패: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=15000, debug=True)