#!/bin/bash

echo "🚀 Flask 앱 배포 시작"

cd /stock4u/stock4u_backend_flask || { echo "❌ 디렉토리 이동 실패"; exit 1; }

# 의존성 설치
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
else
    echo "⚠️ requirements.txt 파일이 없습니다. 의존성 설치를 건너뜁니다."
fi

# 기존 Flask 프로세스 종료 (실행 중이면 종료)
pkill -f app.py || true

# 백그라운드로 실행
nohup python3 app.py > flask.log 2>&1 &

echo "✅ 배포 완료"