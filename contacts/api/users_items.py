from fastapi import APIRouter, Depends, HTTPException, status, Security
from dependencies.database import get_db, SessionLocal
from dependencies.auth import create_access_token, create_refresh_token, decode_refresh_token
from schemas.users_schema import User, TokenModel
from services.user_service import UserService
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer

router = APIRouter()
security = HTTPBearer()


@router.post("/register/", status_code=status.HTTP_201_CREATED)
async def register(user: User, db: SessionLocal = Depends(get_db)):
    user_service = UserService(db)
    exist_user = user_service.get_by_email(user.email)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    return user_service.create_new(user)


@router.post('/login/')
async def login(body: OAuth2PasswordRequestForm = Depends(), db: SessionLocal = Depends(get_db)):
    user_service = UserService(db)
    user = user_service.get_by_email(body.username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user_service.verify_password(user.email, body.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    access_token = await create_access_token(user.email)
    refresh_token = await create_refresh_token(user.email)
    user_service.update_token(user, refresh_token)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security),
                        db: SessionLocal = Depends(get_db)):
    token = credentials.credentials
    email = await decode_refresh_token(token)
    user_service = UserService(db)
    user = user_service.get_user_by_email(email)
    if user_service.get_user_refresh_token(user) != token:
        user_service.update_token(user, None)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await create_access_token(data={"sub": email})
    refresh_token = await create_refresh_token(data={"sub": email})
    user_service.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
