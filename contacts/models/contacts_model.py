from sqlalchemy import Column, String, Date, Boolean
from .base import BaseModel, Base
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.orm import relationship
from .user import UserModel


class ContactModel(BaseModel):
    __tablename__ = 'contacts'

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String)
    phone_number = Column(String, nullable=False)
    birthday = Column(Date)
    favorite = Column(Boolean, default=False)
    user_email = Column('user_email', ForeignKey('users.email', ondelete='CASCADE'), default=None)
    user = relationship('UserModel', backref="contacts")
