import os
import hashlib
from models.user import UserModel


class UserRepo():
    def __init__(self, db) -> None:
        self.db = db

    def create(self, user):
        password, salt = self.hash_password(user.password)
        new_user = UserModel(**user.dict())
        new_user.password = password
        new_user.salt = salt
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

    def activate_user(self, email):
        user = self.get_by_email(email)
        user.confirmed = True
        self.db.commit()

    def generate_salt(self):
        return os.urandom(16)

    def hash_password(self, password, salt=None):
        if salt is None:
            salt = self.generate_salt()
        else:
            salt = bytes.fromhex(salt)
        salted_password = password.encode() + salt
        hashed_password = hashlib.sha256(salted_password).hexdigest()
        return str(hashed_password), str(salt.hex())

    def get_by_email(self, email):
        return self.db.query(UserModel).filter(UserModel.email == email).first()

    def verify_password(self, user_email, input_password):
        user = self.get_by_email(user_email)
        user_password = user.password
        user_salt = user.salt
        hashed_pass, _ = self.hash_password(password=input_password, salt=user_salt)
        return hashed_pass == user_password

    def update_token(self, user_email, refresh_token):
        user = self.get_by_email(user_email)
        user.refresh_token = refresh_token
        self.db.commit()

    def get_user_refresh_token(self, user):
        user_from_db = self.db.query(UserModel).filter(UserModel.email == user.dict()['email']).first()
        return user_from_db.refresh_token

    def update_image(self, email, url):
        user_to_update = self.db.query(UserModel).filter(UserModel.email == email).first()
        user_to_update.image = url
        return user_to_update
