import requests
from fastapi import FastAPI, HTTPException, Response, status, Depends, Cookie
from pydantic import BaseModel
from passlib.context import CryptContext
from uuid import uuid4
from fastapi.middleware.cors import CORSMiddleware

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI(debug=True)

session_data = {}


class Query(BaseModel):
    model: str = "IT-assistant"
    prompt: str = "Hello?"


class UserModel(BaseModel):
    username: str


def generate_session_id():
    return str(uuid4())


@app.post("/login/")
async def login(name: UserModel):
    if name.username != "kb" or name.username == "":
        raise HTTPException(status_code=401, detail="Invalid credentials")

    session_id = generate_session_id()
    session_data[session_id] = {"username": name.username}
    response = {"session_id": session_id}
    return {"message": "Login successful"}


@app.post("/ask")
async def ask(query: Query):
    try:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": query.model,
            "prompt": query.prompt
        })

        # 응답 상태 선검사
        response.raise_for_status()

        # print("Response content", response.content)
        json_response = response.json()
        return {"ask": json_response["response"]}

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error communicating with Ollama: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"JSON decoding failed!: {str(e)}")


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


origins = [
    "http://localhost:4000",  # React 앱이 실행되는 주소
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 요청을 허용할 출처
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
