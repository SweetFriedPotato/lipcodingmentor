<!-- 음성 개발을 위한 핵심 지시사항 -->
**기술 스택**
- 백엔드: FastAPI (Python 3.10+)
- 프론트엔드: React.js (v18+)
- 데이터베이스: SQLite (내장 DB)
- 인증: JWT (RFC 7519 표준)

**음성 명령 사전**
- "API 생성": `/api` 경로로 시작하는 FastAPI 엔드포인트 생성
- "컴포넌트 스캐폴딩": React 컴포넌트 기본 구조 생성
- "JWT 미들웨어": JWT 검증 미들웨어 코드 생성
- "이미지 핸들러": 프로필 이미지 업로드/처리 로직 생성

**코드 생성 규칙**
1. 모든 API 경로는 `/api`로 시작
2. JWT 클레임 필드:
   - 필수: iss, sub, aud, exp, nbf, iat, jti
   - 커스텀: name, email, role(mentor/mentee)
3. 프로필 이미지:
   - 기본 URL: https://placehold.co/500x500.jpg?text=MENTOR (멘토)
   - 크기 제한: 1MB 이하
   - 형식: .jpg, .png만 허용

