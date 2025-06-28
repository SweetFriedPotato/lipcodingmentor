# 🌟 멘토링 커넥트

**멘토와 멘티를 연결하는 스마트한 매칭 플랫폼**

이 앱은 멘토와 멘티를 서로 매칭하는 시스템입니다. 멘토는 자신의 기술 스택과 소개를 등록하고, 멘티는 원하는 멘토에게 매칭 요청을 보낼 수 있습니다.

## 기술 스택

- **백엔드**: FastAPI (Python 3.9+)
- **프론트엔드**: React.js (TypeScript)
- **데이터베이스**: SQLite
- **인증**: JWT (RFC 7519 표준)

## 주요 기능

1. **회원가입 및 로그인**
   - 이메일, 비밀번호, 역할(멘토/멘티) 기반 회원가입
   - JWT 토큰 기반 인증

2. **사용자 프로필**
   - 프로필 이미지 업로드 (.jpg, .png, 1MB 이하)
   - 멘토: 이름, 소개글, 기술 스택 등록
   - 멘티: 이름, 소개글 등록

3. **멘토 목록 조회**
   - 기술 스택으로 필터링
   - 이름 또는 기술 스택으로 정렬

4. **매칭 요청 시스템**
   - 멘티가 멘토에게 요청 전송
   - 멘토가 요청 수락/거절
   - 한 멘토당 한 멘티만 매칭 가능

## 설치 및 실행

### 필요사항

- Python 3.9+
- Node.js 14+
- npm

### 간편 실행

#### 전체 시스템 실행
```bash
./start.sh
```

#### 개별 서버 실행
```bash
# 백엔드만 실행
./run_backend.sh

# 프론트엔드만 실행 (새 터미널에서)
./run_frontend.sh
```

### 수동 실행

#### 백엔드 실행
```bash
cd backend
/Users/jiheeandcats/lipcodingmentor/.venv/bin/python main.py
```

#### 프론트엔드 실행
```bash
cd frontend
npm start
```

## 접속 URL

- **프론트엔드**: http://localhost:3000
- **백엔드 API**: http://localhost:8080
- **Swagger UI**: http://localhost:8080/swagger-ui

## API 명세

모든 API 엔드포인트는 `/api` 경로로 시작합니다.

### 인증
- `POST /api/signup`: 회원가입
- `POST /api/login`: 로그인

### 사용자 정보
- `GET /api/me`: 내 정보 조회
- `PUT /api/profile`: 프로필 수정
- `GET /api/images/{role}/{id}`: 프로필 이미지

### 멘토 목록
- `GET /api/mentors`: 멘토 목록 조회

### 매칭 요청
- `POST /api/match-requests`: 매칭 요청 생성
- `GET /api/match-requests/incoming`: 받은 요청 목록 (멘토용)
- `GET /api/match-requests/outgoing`: 보낸 요청 목록 (멘티용)
- `PUT /api/match-requests/{id}/accept`: 요청 수락
- `PUT /api/match-requests/{id}/reject`: 요청 거절
- `DELETE /api/match-requests/{id}`: 요청 취소

## JWT 클레임

RFC 7519 표준에 따른 클레임 포함:
- `iss`: issuer
- `sub`: subject (사용자 ID)
- `aud`: audience
- `exp`: expiration time (1시간)
- `nbf`: not before
- `iat`: issued at
- `jti`: JWT ID
- `name`: 사용자 이름
- `email`: 이메일
- `role`: 역할 (mentor/mentee)

## 보안 고려사항

- SQL 인젝션 방지 (SQLAlchemy ORM 사용)
- XSS 방지 (React의 기본 이스케이핑)
- JWT 토큰 기반 인증
- 프로필 이미지 크기 및 형식 검증

## 프로젝트 구조

```
lipcodingmentor/
├── backend/
│   ├── main.py              # FastAPI 메인 애플리케이션
│   ├── requirements.txt     # Python 의존성
│   └── mentor_mentee.db     # SQLite 데이터베이스 (자동 생성)
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/      # React 컴포넌트
│   │   ├── contexts/        # React Context
│   │   ├── services/        # API 서비스
│   │   ├── types/           # TypeScript 타입 정의
│   │   └── App.tsx          # 메인 앱 컴포넌트
│   └── package.json         # Node.js 의존성
├── start.sh                 # 실행 스크립트
└── README.md               # 프로젝트 문서
```

## 환경 설정

### 환경 변수 (선택사항)
백엔드에서 사용할 수 있는 환경 변수:

```bash
# JWT 시크릿 키 (기본값: "your-secret-key-here")
export SECRET_KEY="your-production-secret-key"

# 데이터베이스 URL (기본값: SQLite)
export DATABASE_URL="sqlite:///./mentor_mentee.db"
```

### 개발 환경 권장사항
- Python 3.9 이상
- Node.js 16 이상
- 8GB RAM 이상
- 충분한 디스크 공간 (프로필 이미지 저장용)

## 문제 해결

### 백엔드가 시작되지 않는 경우
1. Python 가상환경이 활성화되었는지 확인
2. 필요한 패키지가 모두 설치되었는지 확인:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

### 프론트엔드가 시작되지 않는 경우
1. Node.js 버전 확인 (14+ 필요)
2. 의존성 재설치:
   ```bash
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

### CORS 오류가 발생하는 경우
- 백엔드와 프론트엔드가 각각 8080, 3000 포트에서 실행되고 있는지 확인
- 다른 포트를 사용하는 경우 backend/main.py의 CORS 설정 수정

## 라이선스

This project is licensed under the MIT License.
