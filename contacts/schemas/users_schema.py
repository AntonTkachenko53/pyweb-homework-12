from pydantic import BaseModel, EmailStr


class EmailSchema(BaseModel):
    email: EmailStr


class User(BaseModel):
    email: str
    password: str
    is_active: bool | None
    otp: str | None
    image: str | None

    class Config:
        from_attributes = True
        from_orm = True


class UserActivation(BaseModel):
    email: EmailStr
    otp: str


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
