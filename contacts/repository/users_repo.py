import os
import hashlib
from models.user import UserModel


class UserRepo():
    """
    A repository for managing user data.

    :param db: A database session.
    :type db: sqlalchemy.orm.session.Session
    """
    def __init__(self, db) -> None:
        """
        Initialize the UserRepo instance.

        :param db: A database session.
        :type db: sqlalchemy.orm.session.Session
        """
        self.db = db

    def create(self, user):
        """
        Create a new user in the database.

        :param user: User data to create.
        :type user: User
        :return: The newly created user.
        :rtype: UserModel
        """
        password, salt = self.hash_password(user.password)
        new_user = UserModel(**user.dict())
        new_user.password = password
        new_user.salt = salt
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

    def activate_user(self, email):
        """
        Activate a user account.

        :param email: The email of the user to activate.
        :type email: str
        """
        user = self.get_by_email(email)
        user.confirmed = True
        self.db.commit()

    def generate_salt(self):
        """
        Generate a random salt.

        :return: The generated salt.
        :rtype: bytes
        """
        return os.urandom(16)

    def hash_password(self, password, salt=None):
        """
        Hash a password with optional salt.

        :param password: The password to hash.
        :type password: str
        :param salt: Optional salt value.
        :type salt: bytes, optional
        :return: The hashed password and the salt.
        :rtype: tuple[str, str]
        """
        if salt is None:
            salt = self.generate_salt()
        else:
            salt = bytes.fromhex(salt)
        salted_password = password.encode() + salt
        hashed_password = hashlib.sha256(salted_password).hexdigest()
        return str(hashed_password), str(salt.hex())

    def get_by_email(self, email):
        """
        Retrieve a user by email.

        :param email: The email of the user to retrieve.
        :type email: str
        :return: The user object if found, else None.
        :rtype: UserModel | None
        """
        return self.db.query(UserModel).filter(UserModel.email == email).first()

    def verify_password(self, user_email, input_password):
        """
        Verify a user's password.

        :param user_email: The email of the user.
        :type user_email: str
        :param input_password: The password to verify.
        :type input_password: str
        :return: True if the password is correct, False otherwise.
        :rtype: bool
        """
        user = self.get_by_email(user_email)
        user_password = user.password
        user_salt = user.salt
        hashed_pass, _ = self.hash_password(password=input_password, salt=user_salt)
        return hashed_pass == user_password

    def update_token(self, user_email, refresh_token):
        """
        Update the refresh token for a user.

        :param user_email: The email of the user.
        :type user_email: str
        :param refresh_token: The new refresh token.
        :type refresh_token: str
        """
        user = self.get_by_email(user_email)
        user.refresh_token = refresh_token
        self.db.commit()

    def get_user_refresh_token(self, user):
        """
        Retrieve the refresh token for a user.

        :param user: The user object.
        :type user: UserModel
        :return: The refresh token.
        :rtype: str
        """
        user_from_db = self.db.query(UserModel).filter(UserModel.email == user.dict()['email']).first()
        return user_from_db.refresh_token

    def update_image(self, email, url):
        """
        Update the image URL for a user.

        :param email: The email of the user.
        :type email: str
        :param url: The new image URL.
        :type url: str
        :return: The updated user object.
        :rtype: UserModel
        """
        user_to_update = self.db.query(UserModel).filter(UserModel.email == email).first()
        user_to_update.image = url
        return user_to_update
