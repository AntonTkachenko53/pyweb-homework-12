from pydantic import BaseModel
from datetime import date
from typing import Optional


class Contact(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: Optional[str]
    phone_number: str
    birthday: Optional[date]
    favorite: Optional[bool]

    class Config:
        orm_mode = True
        from_attributes = True


class ContactCreate(BaseModel):
    first_name: str
    last_name: str | None
    phone_number: str | None


class ContactUpdate(BaseModel):
    first_name: str | None
    last_name: str | None
    email: str | None
    phone_number: str | None
    birthday: date | None
    favorite: bool | None
