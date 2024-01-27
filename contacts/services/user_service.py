from repository.users_repo import UserRepo
from schemas.users_schema import User
from models.user import UserModel

from fastapi import HTTPException


class UserService():
    def __init__(self, db) -> None:
        self.repo = UserRepo(db=db)

    def create_new(self, user: User) -> User:
        new_user_from_db = self.repo.create(user)
        if new_user_from_db:
            new_user = User.from_orm(new_user_from_db)
            return new_user
        else:
            return None

    def get_by_email(self, email):
        user_from_db = self.repo.get_by_email(email)
        if user_from_db:
            user = User.from_orm(user_from_db)
            return user
        else:
            return None

    def verify_password(self, user_email, input_password):
        return self.repo.verify_password(user_email, input_password)

    def update_token(self, user, refresh_token):
        self.repo.update_token(user.email, refresh_token)

    def get_user_refresh_token(self, user: User):
        return self.repo.get_user_refresh_token(user)
