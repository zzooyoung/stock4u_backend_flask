import numpy as np
import yfinance as yf
import datetime
import os
import json
from config import TICKERS  # config.py에서 리스트 불러옴

# 설정
target_date = datetime.datetime.today()
window_size = 30

# 저장 폴더 생성
output_dir = "input_data"
os.makedirs(output_dir, exist_ok=True)

for ticker in TICKERS:
    print(f"\n📦 {ticker} 처리 중...")

    # 30일치 과거 데이터 불러오기
    start_date = target_date - datetime.timedelta(days=60)
    end_date = target_date + datetime.timedelta(days=1)
    df = yf.download(ticker, start=start_date, end=end_date)

    # 필요한 특성만 선택
    features = ['Close', 'High', 'Low', 'Open', 'Volume']
    data = df[features].dropna()
    data = data.iloc[-window_size:]

    if len(data) < window_size:
        print(f"❌ {ticker}: 30일치 데이터 부족 ({len(data)}일)")
        continue

    # 모델 입력 형식 맞추기
    X_input = data.values.astype(np.float32).reshape(1, window_size, 5)

    # 파일명과 경로 구성
    output_path = os.path.join(output_dir, f"{ticker}_input.json")

    # JSON 저장
    input_data = {
        "instances": X_input.tolist()
    }
    with open(output_path, "w") as f:
        json.dump(input_data, f, indent=2)

    print(f"✅ 저장 완료: {output_path}")