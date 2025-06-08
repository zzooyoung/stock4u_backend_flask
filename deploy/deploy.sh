#!/bin/bash

echo "🚀 Flask 앱 배포 시작"

cd /stock4u/stock4u_backend_flask

# 의존성 설치
pip install -r requirements.txt

# 기존 서버 종료 (app.py 실행 중이면 종료)
pkill -f app.py || true

# 백그라운드로 실행
nohup python3 app.py > flask.log 2>&1 &

echo "✅ 배포 완료"