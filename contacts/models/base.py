from dependencies.database import Base
from sqlalchemy import Column, Integer


class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
