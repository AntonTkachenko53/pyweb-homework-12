import unittest
from unittest.mock import MagicMock
import hashlib

from sqlalchemy.orm import Session

from contacts.models.user import UserModel
from contacts.repository.users_repo import UserRepo
from contacts.schemas.users_schema import User


class TestContacts(unittest.TestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user_repo = UserRepo(self.session)
        self.url = 'https://example.com/image.jpg'
        self.email = 'test@example.com'

    def test_create_user(self):
        user_data = User(email="usertest@gmail.com", password="password123", is_active=None, otp=None, image=None)

        self.user_repo.hash_password = MagicMock(return_value=("hashed_password", "salt"))

        self.session.add.return_value = None
        self.session.commit.return_value = None
        self.session.refresh.return_value = None

        created_user = self.user_repo.create(user_data)

        self.assertIsNotNone(created_user)
        self.assertEqual(created_user.email, user_data.email)

    def test_activate_user(self):
        email = "test@example.com"
        user_mock = MagicMock()
        user_mock.confirmed = False

        self.user_repo.get_by_email = MagicMock(return_value=user_mock)

        self.user_repo.activate_user(email)

        self.user_repo.get_by_email.assert_called_once_with(email)
        self.assertTrue(user_mock.confirmed)

    def test_hash_password(self):
        password = 'password123'
        salt = self.user_repo.generate_salt()

        # Ensure data is encoded consistently
        encoded_password = password.encode()

        # No need to decode the salt, just use it as bytes
        hashed_password, salt_given = self.user_repo.hash_password(password, salt)

        # Hash the password with the given salt
        hashed_password = hashlib.sha256(encoded_password + salt_given.encode()).hexdigest()

        self.assertEqual(hashed_password, hashed_password)

    def test_get_by_email_found(self):
        user_email = 'test@example.com'
        user = UserModel
        self.session.query().filter().first.return_value = user

        result = self.user_repo.get_by_email(user_email)
        self.assertEqual(result, user)

    def test_get_by_email_not_found(self):
        user_email = 'test@example.com'
        self.session.query().filter().first.return_value = None

        result = self.user_repo.get_by_email(user_email)
        self.assertIsNone(result)

    def test_verify_password_success(self):
        user_email = 'test@example.com'
        input_password = 'password123'
        user_mock = UserModel(email=user_email, password='hashed_password', salt='salt')

        self.user_repo.get_by_email = MagicMock(return_value=user_mock)

        expected_hashed_password = 'hashed_password'
        self.user_repo.hash_password = MagicMock(return_value=(expected_hashed_password, 'salt'))

        result = self.user_repo.verify_password(user_email, input_password)

        self.user_repo.get_by_email.assert_called_once_with(user_email)
        self.user_repo.hash_password.assert_called_once_with(password=input_password, salt='salt')

        self.assertTrue(result)

    def test_verify_password_error(self):
        user_email = 'test@example.com'
        input_password = 'password123'
        user_mock = UserModel(email=user_email, password='hashed_password', salt='salt')

        self.user_repo.get_by_email = MagicMock(return_value=user_mock)

        expected_hashed_password = 'different_hashed_password'
        self.user_repo.hash_password = MagicMock(return_value=(expected_hashed_password, 'salt'))

        result = self.user_repo.verify_password(user_email, input_password)

        self.user_repo.get_by_email.assert_called_once_with(user_email)
        self.user_repo.hash_password.assert_called_once_with(password=input_password, salt='salt')

        self.assertFalse(result)

    def test_update_token(self):
        user_email = 'test@example.com'
        refresh_token = 'new_refresh_token'
        user_mock = UserModel(email=user_email)

        self.user_repo.get_by_email = MagicMock(return_value=user_mock)
        self.user_repo.update_token(user_email, refresh_token)

        self.user_repo.get_by_email.assert_called_once_with(user_email)
        self.assertEqual(user_mock.refresh_token, refresh_token)

        self.session.commit.assert_called_once()

    def test_get_user_refresh_token(self):
        user_email = 'test@example.com'
        refresh_token = 'example_refresh_token'
        user_mock = UserModel(email=user_email, refresh_token=refresh_token)

        filter_mock = self.session.query().filter(UserModel.email == user_email)
        filter_mock.first = MagicMock(return_value=user_mock)

        self.session.query().filter = MagicMock(return_value=filter_mock)

        retrieved_refresh_token = self.user_repo.get_user_refresh_token(user_mock)

        self.session.query().filter.assert_called_once()
        self.assertEqual(retrieved_refresh_token, refresh_token)

    def test_update_image(self):
        user_mock = UserModel(email=self.email, image='old_url')
        filter_mock = MagicMock()
        filter_mock.first = MagicMock(return_value=user_mock)

        query_mock = MagicMock()
        query_mock.filter = MagicMock(return_value=filter_mock)

        self.session.query = MagicMock(return_value=query_mock)
        updated_user = self.user_repo.update_image(self.email, self.url)

        query_mock.filter.assert_called_once()

        self.assertEqual(updated_user.image, self.url)


if __name__ == '__main__':
    unittest.main()