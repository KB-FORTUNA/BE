from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
app = FastAPI(debug=True)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

