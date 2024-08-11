import os
import requests
from fastapi import FastAPI, HTTPException, Response, status, Depends, Cookie
from pydantic import BaseModel, validator
from passlib.context import CryptContext
from uuid import uuid4
from fastapi.middleware.cors import CORSMiddleware

# 환경 변수 로드 (필요 시 dotenv 사용)
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api")

# 비밀번호 암호화 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI(debug=True)

# 세션 데이터 관리
session_data = {}

# 상수로 에러 메시지 관리
INVALID_CREDENTIALS = "Invalid credentials"
USERNAME_CANNOT_BE_EMPTY = "Username cannot be empty"

# 데이터 모델 정의
class Query(BaseModel):
    model: str = "IT-assistant"
    prompt: str = "Hello?"

class UserModel(BaseModel):
    username: str

    @validator("username")
    def username_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError(USERNAME_CANNOT_BE_EMPTY)
        return v

# 세션 ID 생성 함수
def generate_session_id():
    return str(uuid4())

# 로그인 엔드포인트
@app.post("/login/")
async def login(user: UserModel, response: Response):
    # 사용자 인증 (간단한 하드코딩 예시)
    if user.username != "kb":
        raise HTTPException(status_code=401, detail=INVALID_CREDENTIALS)

    # 세션 ID 생성 및 저장
    session_id = generate_session_id()
    session_data[session_id] = {"username": user.username}

    # 세션 쿠키 설정
    response.set_cookie(key="session_id", value=session_id, httponly=True, secure=False, samesite="lax")

    return {"message": "Login successful"}

# 보호된 질문 응답 엔드포인트
@app.post("/ask")
async def ask(query: Query, session_id: str = Cookie(None)):
    # 세션 유효성 검사
    if session_id not in session_data:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        response = requests.post(f"{OLLAMA_API_URL}/generate", json={
            "model": query.model,
            "prompt": query.prompt
        })

        response.raise_for_status()

        json_response = response.json()
        return {"ask": json_response["response"]}

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error communicating with Ollama: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"JSON decoding failed!: {str(e)}")

# 루트 경로
@app.get("/")
async def root():
    return {"message": "Hello World"}

# 개인화된 인사말 경로
@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

# CORS 설정
origins = [
    "http://localhost:4000",  # React 앱이 실행되는 주소
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Uvicorn 서버 실행
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)