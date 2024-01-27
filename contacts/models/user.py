from sqlalchemy import Column, String

from .base import BaseModel, Base


class UserModel(BaseModel):
    __tablename__ = "users"
    
    email = Column(String)
    password = Column(String)
    salt = Column(String)
    refresh_token = Column(String(255), nullable=True)
