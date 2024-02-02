from sqlalchemy import Column, String, Boolean

from .base import BaseModel, Base


class UserModel(BaseModel):
    __tablename__ = "users"
    
    email = Column(String)
    password = Column(String)
    salt = Column(String)
    refresh_token = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
    otp = Column(String)
    image = Column(String)
