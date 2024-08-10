from pydantic import BaseModel


class UserInDB(BaseModel):
    userId: str
    userPassword: str


class UserModel(BaseModel):
    userId: str
