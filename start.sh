#!/bin/bash

# 백엔드 서버 시작
echo "백엔드 서버 시작 중..."
cd backend
/Users/jiheeandcats/lipcodingmentor/.venv/bin/python main.py &
BACKEND_PID=$!

# 프론트엔드 서버 시작
echo "프론트엔드 서버 시작 중..."
cd ../frontend
npm start &
FRONTEND_PID=$!

echo "서버가 시작되었습니다."
echo "백엔드: http://localhost:8080"
echo "프론트엔드: http://localhost:3000"
echo ""
echo "종료하려면 Ctrl+C를 누르세요."

# 신호 처리
trap 'kill $BACKEND_PID $FRONTEND_PID; exit' INT

# 대기
wait
