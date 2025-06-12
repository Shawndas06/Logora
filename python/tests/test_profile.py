import pytest
from fastapi import status
from datetime import datetime, timedelta

def test_get_user_profile(client, test_user_token):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    response = client.get("/profile", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert "email" in response.json()
    assert "full_name" in response.json()
    assert "is_active" in response.json()
    assert "is_verified" in response.json()

def test_get_user_profile_unauthorized(client):
    response = client.get("/profile")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_update_user_profile(client, test_user_token):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    update_data = {
        "full_name": "Updated Name",
        "phone": "+1234567890"
    }
    response = client.put("/profile", json=update_data, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["full_name"] == update_data["full_name"]
    assert response.json()["phone"] == update_data["phone"]

def test_update_user_profile_unauthorized(client):
    update_data = {"full_name": "Updated Name"}
    response = client.put("/profile", json=update_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_update_user_profile_invalid_data(client, test_user_token):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    update_data = {
        "email": "invalid-email",  # Invalid email format
        "phone": "invalid-phone"   # Invalid phone format
    }
    response = client.put("/profile", json=update_data, headers=headers)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_change_password(client, test_user_token):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    password_data = {
        "current_password": "Test123!",
        "new_password": "NewTest123!",
        "confirm_password": "NewTest123!"
    }
    response = client.put("/profile/password", json=password_data, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert "password changed" in response.json()["message"].lower()

def test_change_password_unauthorized(client):
    password_data = {
        "current_password": "Test123!",
        "new_password": "NewTest123!",
        "confirm_password": "NewTest123!"
    }
    response = client.put("/profile/password", json=password_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_change_password_wrong_current(client, test_user_token):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    password_data = {
        "current_password": "WrongPassword",
        "new_password": "NewTest123!",
        "confirm_password": "NewTest123!"
    }
    response = client.put("/profile/password", json=password_data, headers=headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "current password" in response.json()["detail"].lower()

def test_change_password_mismatch(client, test_user_token):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    password_data = {
        "current_password": "Test123!",
        "new_password": "NewTest123!",
        "confirm_password": "DifferentPassword"
    }
    response = client.put("/profile/password", json=password_data, headers=headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "match" in response.json()["detail"].lower()

def test_change_password_weak(client, test_user_token):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    password_data = {
        "current_password": "Test123!",
        "new_password": "weak",
        "confirm_password": "weak"
    }
    response = client.put("/profile/password", json=password_data, headers=headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "password" in response.json()["detail"].lower()

def test_request_password_reset(client):
    reset_data = {"email": "test@example.com"}
    response = client.post("/reset-password", json=reset_data)
    assert response.status_code == status.HTTP_200_OK
    assert "reset link" in response.json()["message"].lower()

def test_request_password_reset_invalid_email(client):
    reset_data = {"email": "invalid-email"}
    response = client.post("/reset-password", json=reset_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_reset_password(client, test_reset_token):
    reset_data = {
        "token": test_reset_token,
        "new_password": "NewTest123!",
        "confirm_password": "NewTest123!"
    }
    response = client.post("/reset-password/confirm", json=reset_data)
    assert response.status_code == status.HTTP_200_OK
    assert "password reset" in response.json()["message"].lower()

def test_reset_password_invalid_token(client):
    reset_data = {
        "token": "invalid-token",
        "new_password": "NewTest123!",
        "confirm_password": "NewTest123!"
    }
    response = client.post("/reset-password/confirm", json=reset_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "invalid" in response.json()["detail"].lower()

def test_reset_password_mismatch(client, test_reset_token):
    reset_data = {
        "token": test_reset_token,
        "new_password": "NewTest123!",
        "confirm_password": "DifferentPassword"
    }
    response = client.post("/reset-password/confirm", json=reset_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "match" in response.json()["detail"].lower()

def test_reset_password_weak(client, test_reset_token):
    reset_data = {
        "token": test_reset_token,
        "new_password": "weak",
        "confirm_password": "weak"
    }
    response = client.post("/reset-password/confirm", json=reset_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "password" in response.json()["detail"].lower()

def test_get_user_notifications(client, test_user_token):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    response = client.get("/profile/notifications", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

def test_get_user_notifications_unauthorized(client):
    response = client.get("/profile/notifications")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_mark_notification_read(client, test_user_token, test_notification):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    response = client.put(f"/profile/notifications/{test_notification.id}/read", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert "marked as read" in response.json()["message"].lower()

def test_mark_notification_read_unauthorized(client, test_notification):
    response = client.put(f"/profile/notifications/{test_notification.id}/read")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_mark_notification_read_not_found(client, test_user_token):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    response = client.put("/profile/notifications/999999/read", headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_delete_notification(client, test_user_token, test_notification):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    response = client.delete(f"/profile/notifications/{test_notification.id}", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert "deleted" in response.json()["message"].lower()

def test_delete_notification_unauthorized(client, test_notification):
    response = client.delete(f"/profile/notifications/{test_notification.id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_delete_notification_not_found(client, test_user_token):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    response = client.delete("/profile/notifications/999999", headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND 