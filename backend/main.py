from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, Response
from sqlalchemy import create_engine, Column, Integer, String, Text, LargeBinary, DateTime, Enum
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import uuid
import base64
import io
from PIL import Image
from typing import Optional, List
import enum
import json

# JWT 설정
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 1

# 데이터베이스 설정
SQLALCHEMY_DATABASE_URL = "sqlite:///./mentor_mentee.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 비밀번호 해싱
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# FastAPI 앱 설정
app = FastAPI(
    title="Mentor-Mentee Matching API",
    description="API for matching mentors and mentees",
    version="1.0.0",
    docs_url="/swagger-ui",
    openapi_url="/openapi.json"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enum 정의
class UserRole(str, enum.Enum):
    MENTOR = "mentor"
    MENTEE = "mentee"

class RequestStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

# 데이터베이스 모델
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(Enum(UserRole))
    name = Column(String)
    bio = Column(Text, default="")
    profile_image = Column(LargeBinary, nullable=True)
    skills = Column(Text, default="")  # JSON string for mentor skills
    created_at = Column(DateTime, default=datetime.utcnow)

class MatchRequest(Base):
    __tablename__ = "match_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    mentor_id = Column(Integer)
    mentee_id = Column(Integer)
    message = Column(Text)
    status = Column(Enum(RequestStatus), default=RequestStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

# Pydantic 모델
class UserSignup(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: UserRole

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    token: str

class ProfileUpdate(BaseModel):
    id: int
    name: str
    role: UserRole
    bio: str
    image: Optional[str] = None
    skills: Optional[List[str]] = None

class UserProfile(BaseModel):
    name: str
    bio: str
    imageUrl: str
    skills: Optional[List[str]] = None

class UserResponse(BaseModel):
    id: int
    email: str
    role: UserRole
    profile: UserProfile

class MatchRequestCreate(BaseModel):
    mentorId: int
    message: str

class MatchRequestResponse(BaseModel):
    id: int
    mentorId: int
    menteeId: int
    message: str
    status: RequestStatus

# 데이터베이스 의존성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 유틸리티 함수
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    now = datetime.utcnow()
    expire = now + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    
    # RFC 7519 표준 클레임 추가
    to_encode.update({
        "iss": "mentor-mentee-app",  # issuer
        "sub": str(data.get("user_id")),  # subject
        "aud": "mentor-mentee-users",  # audience
        "exp": expire,  # expiration time (keep as datetime for python-jose)
        "nbf": now,  # not before (keep as datetime for python-jose)
        "iat": now,  # issued at (keep as datetime for python-jose)
        "jti": str(uuid.uuid4()),  # JWT ID
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        print(f"받은 토큰: {credentials.credentials[:50]}...")  # 디버깅
        payload = jwt.decode(
            credentials.credentials, 
            SECRET_KEY, 
            algorithms=[ALGORITHM],
            options={"verify_aud": False}  # audience 검증 비활성화
        )
        print(f"디코딩된 페이로드: {payload}")  # 디버깅
        user_id: int = int(payload.get("sub"))
        print(f"사용자 ID: {user_id}")  # 디버깅
        if user_id is None:
            print("사용자 ID가 None입니다")  # 디버깅
            raise credentials_exception
    except jwt.JWTError as e:
        print(f"JWT 오류: {e}")  # 디버깅
        raise credentials_exception
    except Exception as e:
        print(f"기타 오류: {e}")  # 디버깅
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        print(f"사용자를 찾을 수 없습니다: {user_id}")  # 디버깅
        raise credentials_exception
    print(f"사용자 발견: {user.email}")  # 디버깅
    return user

def process_image(image_data: str) -> bytes:
    """Base64 이미지를 처리하여 저장 가능한 형태로 변환"""
    try:
        # Base64 디코딩
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # 이미지 크기 및 형식 검증
        if image.format not in ['JPEG', 'PNG']:
            raise HTTPException(status_code=400, detail="Only .jpg and .png formats are allowed")
        
        # 이미지 크기 제한 (500x500 ~ 1000x1000)
        width, height = image.size
        if width < 500 or height < 500 or width > 1000 or height > 1000:
            raise HTTPException(status_code=400, detail="Image size must be between 500x500 and 1000x1000 pixels")
        
        # 정사각형으로 크롭
        min_dimension = min(width, height)
        left = (width - min_dimension) // 2
        top = (height - min_dimension) // 2
        right = left + min_dimension
        bottom = top + min_dimension
        image = image.crop((left, top, right, bottom))
        
        # 500x500으로 리사이즈
        image = image.resize((500, 500), Image.Resampling.LANCZOS)
        
        # 바이트로 변환
        output = io.BytesIO()
        image.save(output, format='JPEG', quality=85)
        return output.getvalue()
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image data: {str(e)}")

# API 라우트
@app.get("/")
async def root():
    return RedirectResponse(url="/swagger-ui")

@app.post("/api/signup", status_code=201)
async def signup(user: UserSignup, db: Session = Depends(get_db)):
    # 이메일 중복 확인
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 사용자 생성
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        role=user.role,
        name=user.name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {"message": "User created successfully"}

@app.post("/api/login", response_model=Token)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token = create_access_token(
        data={
            "user_id": db_user.id,
            "email": db_user.email,
            "name": db_user.name,
            "role": db_user.role
        }
    )
    return {"token": access_token}

@app.get("/api/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    import json
    
    skills = []
    if current_user.role == UserRole.MENTOR and current_user.skills:
        try:
            skills = json.loads(current_user.skills)
        except:
            skills = []
    
    profile = UserProfile(
        name=current_user.name or "",
        bio=current_user.bio or "",
        imageUrl=f"/api/images/{current_user.role}/{current_user.id}",
        skills=skills if current_user.role == UserRole.MENTOR else None
    )
    
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        role=current_user.role,
        profile=profile
    )

@app.get("/api/images/{role}/{user_id}")
async def get_profile_image(role: str, user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.profile_image:
        return Response(content=user.profile_image, media_type="image/jpeg")
    else:
        # 기본 이미지 URL로 리다이렉트
        default_url = f"https://placehold.co/500x500.jpg?text={role.upper()}"
        return RedirectResponse(url=default_url)

@app.put("/api/profile", response_model=UserResponse)
async def update_profile(profile: ProfileUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    import json
    
    # 현재 사용자의 프로필만 수정 가능
    if current_user.id != profile.id:
        raise HTTPException(status_code=403, detail="You can only update your own profile")
    
    # 프로필 업데이트
    current_user.name = profile.name
    current_user.bio = profile.bio
    
    # 이미지 처리
    if profile.image:
        current_user.profile_image = process_image(profile.image)
    
    # 스킬 처리 (멘토만)
    if current_user.role == UserRole.MENTOR and profile.skills:
        current_user.skills = json.dumps(profile.skills)
    
    db.commit()
    db.refresh(current_user)
    
    # 응답 생성
    skills = []
    if current_user.role == UserRole.MENTOR and current_user.skills:
        try:
            skills = json.loads(current_user.skills)
        except:
            skills = []
    
    user_profile = UserProfile(
        name=current_user.name or "",
        bio=current_user.bio or "",
        imageUrl=f"/api/images/{current_user.role}/{current_user.id}",
        skills=skills if current_user.role == UserRole.MENTOR else None
    )
    
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        role=current_user.role,
        profile=user_profile
    )

@app.get("/api/mentors", response_model=List[UserResponse])
async def get_mentors(
    skill: Optional[str] = None,
    order_by: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    import json
    
    # 멘티만 접근 가능
    if current_user.role != UserRole.MENTEE:
        raise HTTPException(status_code=403, detail="Only mentees can view mentors")
    
    query = db.query(User).filter(User.role == UserRole.MENTOR)
    
    # 스킬 필터링
    if skill:
        mentors = query.all()
        filtered_mentors = []
        for mentor in mentors:
            if mentor.skills:
                try:
                    mentor_skills = json.loads(mentor.skills)
                    if any(skill.lower() in s.lower() for s in mentor_skills):
                        filtered_mentors.append(mentor)
                except:
                    continue
        mentors = filtered_mentors
    else:
        mentors = query.all()
    
    # 정렬
    if order_by == "name":
        mentors.sort(key=lambda x: x.name or "")
    elif order_by == "skill":
        mentors.sort(key=lambda x: x.skills or "")
    else:
        mentors.sort(key=lambda x: x.id)
    
    # 응답 생성
    result = []
    for mentor in mentors:
        skills = []
        if mentor.skills:
            try:
                skills = json.loads(mentor.skills)
            except:
                skills = []
        
        profile = UserProfile(
            name=mentor.name or "",
            bio=mentor.bio or "",
            imageUrl=f"/api/images/{mentor.role}/{mentor.id}",
            skills=skills
        )
        
        result.append(UserResponse(
            id=mentor.id,
            email=mentor.email,
            role=mentor.role,
            profile=profile
        ))
    
    return result

@app.post("/api/match-requests", response_model=MatchRequestResponse)
async def create_match_request(
    request: MatchRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 멘티만 요청 생성 가능
    if current_user.role != UserRole.MENTEE:
        raise HTTPException(status_code=403, detail="Only mentees can create match requests")
    
    # 멘토 존재 확인
    mentor = db.query(User).filter(User.id == request.mentorId, User.role == UserRole.MENTOR).first()
    if not mentor:
        raise HTTPException(status_code=400, detail="Mentor not found")
    
    # 중복 요청 확인 (pending 상태의 요청이 있는지)
    existing_pending = db.query(MatchRequest).filter(
        MatchRequest.mentee_id == current_user.id,
        MatchRequest.status == RequestStatus.PENDING
    ).first()
    
    if existing_pending:
        raise HTTPException(status_code=400, detail="You already have a pending request")
    
    # 요청 생성
    match_request = MatchRequest(
        mentor_id=request.mentorId,
        mentee_id=current_user.id,  # JWT 토큰에서 가져온 현재 사용자 ID 사용
        message=request.message,
        status=RequestStatus.PENDING
    )
    
    db.add(match_request)
    db.commit()
    db.refresh(match_request)
    
    return MatchRequestResponse(
        id=match_request.id,
        mentorId=match_request.mentor_id,
        menteeId=match_request.mentee_id,
        message=match_request.message,
        status=match_request.status
    )

@app.get("/api/match-requests/incoming", response_model=List[MatchRequestResponse])
async def get_incoming_requests(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # 멘토만 접근 가능
    if current_user.role != UserRole.MENTOR:
        raise HTTPException(status_code=403, detail="Only mentors can view incoming requests")
    
    requests = db.query(MatchRequest).filter(MatchRequest.mentor_id == current_user.id).all()
    
    return [
        MatchRequestResponse(
            id=req.id,
            mentorId=req.mentor_id,
            menteeId=req.mentee_id,
            message=req.message,
            status=req.status
        )
        for req in requests
    ]

@app.get("/api/match-requests/outgoing", response_model=List[MatchRequestResponse])
async def get_outgoing_requests(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # 멘티만 접근 가능
    if current_user.role != UserRole.MENTEE:
        raise HTTPException(status_code=403, detail="Only mentees can view outgoing requests")
    
    requests = db.query(MatchRequest).filter(MatchRequest.mentee_id == current_user.id).all()
    
    return [
        MatchRequestResponse(
            id=req.id,
            mentorId=req.mentor_id,
            menteeId=req.mentee_id,
            message=req.message,
            status=req.status
        )
        for req in requests
    ]

@app.put("/api/match-requests/{request_id}/accept", response_model=MatchRequestResponse)
async def accept_request(request_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # 멘토만 접근 가능
    if current_user.role != UserRole.MENTOR:
        raise HTTPException(status_code=403, detail="Only mentors can accept requests")
    
    # 요청 찾기
    match_request = db.query(MatchRequest).filter(
        MatchRequest.id == request_id,
        MatchRequest.mentor_id == current_user.id
    ).first()
    
    if not match_request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # 이미 수락된 요청이 있는지 확인
    existing_accepted = db.query(MatchRequest).filter(
        MatchRequest.mentor_id == current_user.id,
        MatchRequest.status == RequestStatus.ACCEPTED
    ).first()
    
    if existing_accepted:
        raise HTTPException(status_code=400, detail="You can only accept one request at a time")
    
    # 요청 수락
    match_request.status = RequestStatus.ACCEPTED
    db.commit()
    db.refresh(match_request)
    
    return MatchRequestResponse(
        id=match_request.id,
        mentorId=match_request.mentor_id,
        menteeId=match_request.mentee_id,
        message=match_request.message,
        status=match_request.status
    )

@app.put("/api/match-requests/{request_id}/reject", response_model=MatchRequestResponse)
async def reject_request(request_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # 멘토만 접근 가능
    if current_user.role != UserRole.MENTOR:
        raise HTTPException(status_code=403, detail="Only mentors can reject requests")
    
    # 요청 찾기
    match_request = db.query(MatchRequest).filter(
        MatchRequest.id == request_id,
        MatchRequest.mentor_id == current_user.id
    ).first()
    
    if not match_request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # 요청 거절
    match_request.status = RequestStatus.REJECTED
    db.commit()
    db.refresh(match_request)
    
    return MatchRequestResponse(
        id=match_request.id,
        mentorId=match_request.mentor_id,
        menteeId=match_request.mentee_id,
        message=match_request.message,
        status=match_request.status
    )

@app.delete("/api/match-requests/{request_id}", response_model=MatchRequestResponse)
async def cancel_request(request_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # 멘티만 접근 가능
    if current_user.role != UserRole.MENTEE:
        raise HTTPException(status_code=403, detail="Only mentees can cancel requests")
    
    # 요청 찾기
    match_request = db.query(MatchRequest).filter(
        MatchRequest.id == request_id,
        MatchRequest.mentee_id == current_user.id
    ).first()
    
    if not match_request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # 요청 취소
    match_request.status = RequestStatus.CANCELLED
    db.commit()
    db.refresh(match_request)
    
    return MatchRequestResponse(
        id=match_request.id,
        mentorId=match_request.mentor_id,
        menteeId=match_request.mentee_id,
        message=match_request.message,
        status=match_request.status
    )

@app.post("/api/admin/reset-database")
async def reset_database(db: Session = Depends(get_db)):
    """데이터베이스 초기화 및 샘플 멘토 5명 생성"""
    try:
        # 모든 데이터 삭제
        db.query(MatchRequest).delete()
        db.query(User).delete()
        db.commit()
        
        # 샘플 멘토 5명 생성
        mentors_data = [
            {
                "email": "mentor1@example.com",
                "password": "password123",
                "name": "김개발",
                "role": "mentor",
                "bio": "10년 경력의 풀스택 개발자입니다. React, Node.js, Python 전문가입니다.",
                "skills": ["React", "Node.js", "Python", "TypeScript", "AWS"]
            },
            {
                "email": "mentor2@example.com", 
                "password": "password123",
                "name": "이디자인",
                "role": "mentor",
                "bio": "UI/UX 디자이너이자 프론트엔드 개발자입니다. 사용자 경험을 중시합니다.",
                "skills": ["UI/UX", "Figma", "React", "CSS", "JavaScript"]
            },
            {
                "email": "mentor3@example.com",
                "password": "password123", 
                "name": "박데이터",
                "role": "mentor",
                "bio": "데이터 사이언티스트이자 머신러닝 엔지니어입니다. AI 전문가입니다.",
                "skills": ["Python", "TensorFlow", "PyTorch", "SQL", "Machine Learning"]
            },
            {
                "email": "mentor4@example.com",
                "password": "password123",
                "name": "최모바일", 
                "role": "mentor",
                "bio": "iOS/Android 앱 개발 전문가입니다. 크로스 플랫폼 개발 경험이 풍부합니다.",
                "skills": ["Swift", "Kotlin", "React Native", "Flutter", "iOS"]
            },
            {
                "email": "mentor5@example.com",
                "password": "password123",
                "name": "정클라우드",
                "role": "mentor", 
                "bio": "클라우드 아키텍트이자 DevOps 엔지니어입니다. 인프라 구축 전문가입니다.",
                "skills": ["AWS", "Docker", "Kubernetes", "Terraform", "DevOps"]
            }
        ]
        
        created_mentors = []
        for mentor_data in mentors_data:
            # 비밀번호 해싱
            hashed_password = pwd_context.hash(mentor_data["password"])
            
            # 사용자 생성 (프로필 정보 포함)
            user = User(
                email=mentor_data["email"],
                hashed_password=hashed_password,
                role=UserRole.MENTOR,
                name=mentor_data["name"],
                bio=mentor_data["bio"],
                skills=json.dumps(mentor_data["skills"])
            )
            db.add(user)
            db.flush()
            
            created_mentors.append({
                "id": user.id,
                "email": user.email,
                "name": mentor_data["name"],
                "skills": mentor_data["skills"]
            })
        
        # 샘플 멘티 1명도 생성
        hashed_password = pwd_context.hash("password123")
        mentee = User(
            email="mentee@example.com",
            hashed_password=hashed_password,
            role=UserRole.MENTEE,
            name="김멘티",
            bio="개발을 배우고 싶은 신입 개발자입니다.",
            skills=json.dumps([])
        )
        db.add(mentee)
        
        db.commit()
        
        return {
            "message": "데이터베이스가 성공적으로 초기화되었습니다.",
            "mentors_created": len(created_mentors),
            "mentors": created_mentors,
            "test_mentee": {
                "email": "mentee@example.com",
                "password": "password123",
                "name": "김멘티"
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"데이터베이스 초기화 실패: {str(e)}")

@app.get("/api/images/{user_type}/{user_id}")
async def get_profile_image(user_type: str, user_id: int, db: Session = Depends(get_db)):
    """프로필 이미지 조회 - 없으면 기본 이미지 리디렉션"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            # 기본 이미지로 리디렉션
            if user_type == "mentor":
                return RedirectResponse(url="https://placehold.co/500x500.jpg?text=MENTOR")
            else:
                return RedirectResponse(url="https://placehold.co/500x500.jpg?text=MENTEE")
        
        if user.profile_image:
            # 저장된 이미지가 있으면 반환
            return Response(content=user.profile_image, media_type="image/jpeg")
        else:
            # 저장된 이미지가 없으면 기본 이미지로 리디렉션
            if user.role == UserRole.MENTOR:
                return RedirectResponse(url="https://placehold.co/500x500.jpg?text=MENTOR")
            else:
                return RedirectResponse(url="https://placehold.co/500x500.jpg?text=MENTEE")
    except Exception as e:
        # 에러 발생 시 기본 이미지로 리디렉션
        if user_type == "mentor":
            return RedirectResponse(url="https://placehold.co/500x500.jpg?text=MENTOR")
        else:
            return RedirectResponse(url="https://placehold.co/500x500.jpg?text=MENTEE")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
