from random import randint

from repository.users_repo import UserRepo
from schemas.users_schema import User, UserActivation
from models.user import UserModel
from dependencies.emails import send_email

from fastapi import HTTPException


class UserService():
    """
    Service class for managing users.
    """
    def __init__(self, db) -> None:
        """
        Initialize the UserService instance.

        :param db: A database session.
        :type db: SessionLocal
        """
        self.repo = UserRepo(db=db)

    def create_new(self, user: User) -> User:
        """
        Create a new user and send activation email with OTP.

        :param user: User data for registration.
        :type user: User
        :return: The newly created user.
        :rtype: User
        """
        user.is_active = False
        user.otp = str(randint(100000, 999999))
        send_email('Email activation', f"Your OTP is {user.otp}", user.email)
        new_user_from_db = self.repo.create(user)
        if new_user_from_db:
            new_user = User.from_orm(new_user_from_db)
            return new_user
        else:
            return None

    def get_by_email(self, email):
        """
        Retrieve a user by email.

        :param email: The email of the user.
        :type email: str
        :return: The retrieved user.
        :rtype: User
        """
        user_from_db = self.repo.get_by_email(email)
        if user_from_db:
            user = User.from_orm(user_from_db)
            return user
        else:
            return None

    def activate_user(self, data: UserActivation) -> User:
        """
        Activate a user using OTP.

        :param data: User activation data.
        :type data: UserActivation
        :return: The activated user.
        :rtype: User
        """
        user = self.get_by_email(data.email)
        if data.otp == user.otp:
            user = self.repo.activate_user(user.email)
        return user

    def verify_password(self, user_email, input_password):
        """
        Verify user password.

        :param user_email: The email of the user.
        :type user_email: str
        :param input_password: The password to verify.
        :type input_password: str
        :return: True if password is correct, False otherwise.
        :rtype: bool
        """
        return self.repo.verify_password(user_email, input_password)

    def update_token(self, user, refresh_token):
        """
        Update user's refresh token.

        :param user: The user object.
        :type user: User
        :param refresh_token: The new refresh token.
        :type refresh_token: str
        """
        self.repo.update_token(user.email, refresh_token)

    def get_user_refresh_token(self, user: User):
        """
        Retrieve user's refresh token.

        :param user: The user object.
        :type user: User
        :return: The user's refresh token.
        :rtype: str
        """
        return self.repo.get_user_refresh_token(user)

    def set_image(self, email: str, url: str) -> User:
        """
        Set user's profile image URL.

        :param email: The email of the user.
        :type email: str
        :param url: The URL of the profile image.
        :type url: str
        :return: The updated user.
        :rtype: User
        """
        user_from_db = self.repo.update_image(email, url)
        return User.from_orm(user_from_db)
