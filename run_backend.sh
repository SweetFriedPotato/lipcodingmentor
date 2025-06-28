#!/bin/bash

# 백엔드 실행 스크립트
echo "🚀 백엔드 서버를 시작합니다..."

# 백엔드 디렉토리로 이동
cd backend

# 가상환경 경로 확인
VENV_PATH="../.venv/bin/python"
if [ ! -f "$VENV_PATH" ]; then
    echo "❌ 가상환경을 찾을 수 없습니다: $VENV_PATH"
    echo "다음 명령으로 가상환경을 생성하세요:"
    echo "python -m venv ../.venv"
    echo "source ../.venv/bin/activate"
    echo "pip install -r requirements.txt"
    exit 1
fi

# 의존성이 설치되어 있는지 확인
echo "📦 의존성을 확인하는 중..."
$VENV_PATH -c "import fastapi" 2>/dev/null || {
    echo "❌ FastAPI가 설치되지 않았습니다. 의존성을 설치하는 중..."
    $VENV_PATH -m pip install -r requirements.txt
}

# FastAPI 앱 실행
echo "✨ FastAPI 서버를 실행합니다 (http://localhost:8080)"
echo "📚 Swagger UI: http://localhost:8080/swagger-ui"
$VENV_PATH main.py
