#!/bin/bash

# 프론트엔드 실행 스크립트
echo "🚀 프론트엔드 서버를 시작합니다..."

# 프론트엔드 디렉토리로 이동
cd frontend

# 의존성이 설치되어 있는지 확인
if [ ! -d "node_modules" ]; then
    echo "📦 의존성을 설치하는 중..."
    npm install
fi

# React 앱 실행
echo "✨ React 앱을 실행합니다 (http://localhost:3000)"
npm start
