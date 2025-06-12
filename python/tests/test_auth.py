import pytest
from fastapi import status
from auth import User, hash_password, verify_password

def test_password_hashing():
    password = "Test123!"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("WrongPassword", hashed)

def test_user_registration(client, test_user_data):
    response = client.post("/register", json=test_user_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert "message" in response.json()
    assert "successfully" in response.json()["message"].lower()

def test_user_registration_duplicate_email(client, test_user_data):
    # First registration
    client.post("/register", json=test_user_data)
    
    # Second registration with same email
    response = client.post("/register", json=test_user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in response.json()["detail"].lower()

def test_user_registration_invalid_password(client, test_user_data):
    # Test with weak password
    test_user_data["password"] = "weak"
    response = client.post("/register", json=test_user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "password" in response.json()["detail"].lower()

def test_user_login(client, test_user_credentials):
    response = client.post("/token", data=test_user_credentials)
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_user_login_invalid_credentials(client):
    response = client.post("/token", data={
        "username": "wrong@example.com",
        "password": "WrongPassword"
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "incorrect" in response.json()["detail"].lower()

def test_user_login_unverified(client, test_db):
    # Create unverified user
    unverified_user = User(
        email="unverified@example.com",
        password=hash_password("Test123!"),
        full_name="Unverified User",
        is_active=True,
        is_verified=False
    )
    test_db.add(unverified_user)
    test_db.commit()
    
    # Try to login
    response = client.post("/token", data={
        "username": "unverified@example.com",
        "password": "Test123!"
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "verify" in response.json()["detail"].lower()

def test_user_login_inactive(client, test_db):
    # Create inactive user
    inactive_user = User(
        email="inactive@example.com",
        password=hash_password("Test123!"),
        full_name="Inactive User",
        is_active=False,
        is_verified=True
    )
    test_db.add(inactive_user)
    test_db.commit()
    
    # Try to login
    response = client.post("/token", data={
        "username": "inactive@example.com",
        "password": "Test123!"
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "disabled" in response.json()["detail"].lower()

def test_token_refresh(client, test_user_credentials):
    # First login to get tokens
    login_response = client.post("/token", data=test_user_credentials)
    refresh_token = login_response.json()["refresh_token"]
    
    # Try to refresh token
    response = client.post("/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_token_refresh_invalid(client):
    response = client.post("/refresh", json={"refresh_token": "invalid_token"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "invalid" in response.json()["detail"].lower()

def test_email_verification(client, test_db):
    # Create unverified user with verification token
    verification_token = "test_verification_token"
    unverified_user = User(
        email="verify@example.com",
        password=hash_password("Test123!"),
        full_name="Verify User",
        is_active=True,
        is_verified=False,
        verification_token=verification_token
    )
    test_db.add(unverified_user)
    test_db.commit()
    
    # Verify email
    response = client.get(f"/verify-email/{verification_token}")
    assert response.status_code == status.HTTP_200_OK
    assert "verified" in response.json()["message"].lower()
    
    # Check user is now verified
    user = test_db.query(User).filter(User.email == "verify@example.com").first()
    assert user.is_verified
    assert user.verification_token is None

def test_email_verification_invalid_token(client):
    response = client.get("/verify-email/invalid_token")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "invalid" in response.json()["detail"].lower() 