from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    userId = Column(String, primary_key=True, index=True)
    userPassword = Column(String)
