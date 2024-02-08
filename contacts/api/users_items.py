from fastapi import APIRouter, Depends, HTTPException, status, Security, File, UploadFile
from dependencies.database import get_db, SessionLocal
from depenedencies.rate_limiter import rate_limit
from dependencies.auth import create_access_token, create_refresh_token, decode_refresh_token, get_current_user_email
from schemas.users_schema import User, TokenModel, UserActivation
from services.user_service import UserService
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer

from depenedencies.cloudinary_dep import get_uploader

router = APIRouter()
security = HTTPBearer()


@router.post("/register/", status_code=status.HTTP_201_CREATED)
async def register(user: User, db: SessionLocal = Depends(get_db), rl=Depends(rate_limit)):
    """
        Register a new user.

        :param user: User data for registration.
        :type user: User
        :param db: Database session dependency.
        :type db: SessionLocal
        :param rl: Rate limit dependency.
        :type rl: RateLimiter
        :return: The newly registered user.
        :rtype: User
        """
    user_service = UserService(db)
    exist_user = user_service.get_by_email(user.email)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    return user_service.create_new(user)


@router.post("/activate/", response_model=User)
async def activate(data: UserActivation, db: SessionLocal = Depends(get_db), rl=Depends(rate_limit)):
    """
    Activate a user account.

    :param data: User activation data.
    :type data: UserActivation
    :param db: Database session dependency.
    :type db: SessionLocal
    :param rl: Rate limit dependency.
    :type rl: RateLimiter
    :return: The activated user.
    :rtype: User
    """
    user_service = UserService(db)
    return user_service.activate_user(data)


@router.post('/login/')
async def login(body: OAuth2PasswordRequestForm = Depends(), db: SessionLocal = Depends(get_db)):
    """
        Log in a user.

        :param body: Login request form data.
        :type body: OAuth2PasswordRequestForm
        :param db: Database session dependency.
        :type db: SessionLocal
        :return: Access and refresh tokens.
        :rtype: dict
        """
    user_service = UserService(db)
    user = user_service.get_by_email(body.username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    if not user_service.verify_password(user.email, body.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    access_token = await create_access_token(user.email)
    refresh_token = await create_refresh_token(user.email)
    user_service.update_token(user, refresh_token)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security),
                        db: SessionLocal = Depends(get_db)):
    """
        Refresh access and refresh tokens.

        :param credentials: HTTP authorization credentials.
        :type credentials: HTTPAuthorizationCredentials
        :param db: Database session dependency.
        :type db: SessionLocal
        :return: New access and refresh tokens.
        :rtype: TokenModel
        """
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


@router.post("/upload_image")
def upload(current_email: str = Depends(get_current_user_email), file: UploadFile = File(...),
           uploader=Depends(get_uploader), db: SessionLocal = Depends(get_db)):
    """
        Upload a user profile image.

        :param current_email: The email of the current user.
        :type current_email: str
        :param file: The image file to upload.
        :type file: UploadFile
        :param uploader: The uploader dependency.
        :type uploader: UploadService
        :param db: Database session dependency.
        :type db: SessionLocal
        :return: Success message or error message.
        :rtype: dict
        """
    try:
        user_service = UserService(db)
        contents = file.file.read()
        response = uploader.upload(contents, public_id=file.filename)
        response.get('secure_url')
        user_service.set_image(current_email, response.get('secure_url'))

    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()

    return {"message": f"Successfully uploaded {file.filename}"}
