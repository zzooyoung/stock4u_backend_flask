import numpy as np
import yfinance as yf
import datetime
import tensorflow as tf

# 설정
ticker = "AMZN"
target_date = datetime.datetime.today()
window_size = 30

# 30일치 과거 데이터 불러오기
start_date = target_date - datetime.timedelta(days=60)  # 휴장 포함 여유
end_date = target_date + datetime.timedelta(days=1)
df = yf.download(ticker, start=start_date, end=end_date)

# 필요한 특성만 선택
features = ['Close', 'High', 'Low', 'Open', 'Volume']
data = df[features].dropna()
data = data.iloc[-window_size:]  # 마지막 30일 데이터 추출

if len(data) < window_size:
    raise ValueError("30일치 데이터가 부족합니다.")

# 모델 입력 형식 맞추기
X_input = data.values.astype(np.float32).reshape(1, window_size, 5)

## 저장된 KServe 모델 로드
#import os

## model_path = os.path.join('/home/ubuntu/mnt/data/' , ticker,'1')
#model_path = os.path.join('/home/sa/도전학기/combine-test/' , ticker,'1')
#model = tf.saved_model.load(model_path)
#predict_fn = model.signatures["serving_default"]

## 예측 수행
#pred = predict_fn(tf.constant(X_input))
# pred = model.predict(X_input)
#pred_values = pred["predictions"].numpy()[0]



## 출력
#print(f'\n📈 {ticker} 예측 결과 {end_date.strftime("%Y-%m-%d")}:')
#print(f"Close : {pred_values[0]:.2f}")
#print(f"High  : {pred_values[1]:.2f}")
#print(f"Low   : {pred_values[2]:.2f}")
#print(f"Open  : {pred_values[3]:.2f}")
#print(f"Volume: {int(pred_values[4])}")

import os
import json

# 저장 경로 설정
output_dir = "input_data"
os.makedirs(output_dir, exist_ok=True) # input 폴더가 없으면 생성

# 파일명과 경로 구성 
output_path = os.path.join(output_dir, f"{ticker}_input.json")


# JSON 저장 
input_data = {
    "instances": X_input.tolist()
}
with open(output_path, "w") as f:
    json.dump(input_data, f, indent=2)

print(" {output_path} 저장 완료")