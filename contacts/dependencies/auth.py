from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status, Depends
from dependencies.database import get_db, SessionLocal
from services.user_service import UserService
import datetime
from jose import JWTError, jwt
from dotenv import load_dotenv
import os

load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')


async def create_access_token(email: str):
    token_data = {
        "sub": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
        "scope": "access_token"
    }
    to_encode = token_data.copy()
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return token


async def create_refresh_token(email: str):
    token_data = {
        "sub": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7),
        "scope": "refresh_token"
    }
    to_encode = token_data.copy()
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return token


async def decode_refresh_token(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=ALGORITHM)
        if payload['scope'] == 'refresh_token':
            email = payload['sub']
            return email
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')


async def get_current_user_email(token: str = Depends(oauth2_scheme), db: SessionLocal = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        if payload['scope'] == 'access_token':
            email = payload["sub"]
            if email is None:
                raise credentials_exception
        else:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user_service = UserService(db)
    user = user_service.get_user_by_email(email)
    if user is None:
        raise credentials_exception
    return email
