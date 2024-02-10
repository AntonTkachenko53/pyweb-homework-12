from unittest.mock import MagicMock
from fastapi import status
from contacts.models.user import UserModel
from contacts.services.user_service import UserService


def test_register_user(client, session):
    user_data = {"email": "test@example.com", "password": "password"}
    response = client.post("/register/", json=user_data)
    assert response.status_code == 201
    assert response.json()["email"] == user_data["email"]

    user = session.query(UserModel).filter(UserModel.email == user_data["email"]).first()

    assert user is not None


def test_register_existing_user(client, session):
    existing_user = UserModel(email="existing@example.com", password="password123")
    new_user = UserModel(email="existing@example.com", password="password456")
    session.query().filter().first.return_value = existing_user

    UserService.get_by_email = MagicMock(return_value=existing_user)
    response = client.post("/register/", json=new_user.dict())

    assert response.status_code == status.HTTP_409_CONFLICT


def test_activate(client, session):
    user = UserModel(email="test@example.com")
    session.add(user)
    session.commit()

    activation_data = {"email": user.email, "activation_code": "123456"}
    response = client.post("/activate/", json=activation_data)

    assert response.status_code == 200
    assert response.json()["email"] == user.email
    assert response.json()["confirmed"] is True


def test_login_success(client, session):
    user = UserModel(email="test@example.com", password="password123", confirmed=True)
    login_data = {"username": "test@example.com", "password": "password123"}
    session.query().filter().first.return_value = user

    UserService.get_by_email = MagicMock(return_value=user)
    UserService.verify_password = MagicMock(return_value=True)

    response = client.post("/login/", data=login_data)

    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()


def test_login_invalid_email(client, session):
    login_data = {"username": "invalid@example.com", "password": "password123"}

    response = client.post("/login/", data=login_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Invalid email"


def test_login_unconfirmed_email(client, session):
    user = UserModel(email="test@example.com", password="password123", confirmed=False)
    login_data = {"username": "test@example.com", "password": "password123"}

    session.query().filter().first.return_value = user

    UserService.get_by_email = MagicMock(return_value=user)
    UserService.verify_password = MagicMock(return_value=True)

    response = client.post("/login/", data=login_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Email not confirmed"


def test_login_invalid_password(client, session):
    user = UserModel(email="test@example.com", password="password123", confirmed=True)
    login_data = {"username": "test@example.com", "password": "invalidpassword"}
    session.query().filter().first.return_value = user

    UserService.get_by_email = MagicMock(return_value=user)
    UserService.verify_password = MagicMock(return_value=False)

    response = client.post("/login/", data=login_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Invalid password"


def test_refresh_token_success(client, session):
    refresh_token = "valid_refresh_token"
    user = UserModel(email="test@example.com")
    session.query().filter().first.return_value = user

    UserService.get_user_by_email = MagicMock(return_value=user)
    UserService.get_user_refresh_token = MagicMock(return_value=refresh_token)

    response = client.get("/refresh_token", headers={"Authorization": f"Bearer {refresh_token}"})

    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()


def test_refresh_token_invalid_token(client, session):
    refresh_token = "invalid_refresh_token"
    user = UserModel(email="test@example.com")
    session.query().filter().first.return_value = user

    UserService.get_user_by_email = MagicMock(return_value=user)
    UserService.get_user_refresh_token = MagicMock(return_value="valid_refresh_token")

    response = client.get("/refresh_token", headers={"Authorization": f"Bearer {refresh_token}"})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Invalid refresh token"


def test_upload_image_success(client, session):
    user = UserModel(email="test@example.com")
    session.query().filter().first.return_value = user
    UserService.set_image = MagicMock()
    response = client.post("/upload_image", headers={"Authorization": "Bearer valid_token"},
                           files={"file": ("test.jpg", "test_image_content")})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Successfully uploaded test.jpg"


def test_upload_image_error(client, session):
    UserService.set_image = MagicMock(side_effect=Exception("Test exception"))

    response = client.post("/upload_image", headers={"Authorization": "Bearer valid_token"},
                           files={"file": ("test.jpg", "test_image_content")})

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json()["message"] == "There was an error uploading the file"

