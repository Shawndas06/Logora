import pytest
from fastapi import status
from datetime import datetime, timedelta

def test_get_user_accounts(client, test_user_token):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    response = client.get("/accounts", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

def test_get_user_accounts_unauthorized(client):
    response = client.get("/accounts")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_create_account(client, test_user_token, test_account_data):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    response = client.post("/accounts", json=test_account_data, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    assert "id" in response.json()
    assert response.json()["type"] == test_account_data["type"]
    assert response.json()["number"] == test_account_data["number"]

def test_create_account_duplicate(client, test_user_token, test_account_data):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    # First creation
    client.post("/accounts", json=test_account_data, headers=headers)
    
    # Second creation with same number
    response = client.post("/accounts", json=test_account_data, headers=headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in response.json()["detail"].lower()

def test_create_account_invalid_type(client, test_user_token, test_account_data):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    test_account_data["type"] = "invalid_type"
    response = client.post("/accounts", json=test_account_data, headers=headers)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_get_account_details(client, test_user_token, test_account):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    response = client.get(f"/accounts/{test_account.id}", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == test_account.id
    assert response.json()["type"] == test_account.type
    assert response.json()["number"] == test_account.number

def test_get_account_details_not_found(client, test_user_token):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    response = client.get("/accounts/999999", headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_get_account_details_unauthorized(client, test_account):
    response = client.get(f"/accounts/{test_account.id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_update_account(client, test_user_token, test_account):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    update_data = {
        "status": "inactive",
        "address": "Updated Address"
    }
    response = client.put(f"/accounts/{test_account.id}", json=update_data, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == update_data["status"]
    assert response.json()["address"] == update_data["address"]

def test_update_account_not_found(client, test_user_token):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    update_data = {"status": "inactive"}
    response = client.put("/accounts/999999", json=update_data, headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_delete_account(client, test_user_token, test_account):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    response = client.delete(f"/accounts/{test_account.id}", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert "deleted" in response.json()["message"].lower()

def test_delete_account_not_found(client, test_user_token):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    response = client.delete("/accounts/999999", headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_get_account_history(client, test_user_token, test_account):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    response = client.get(f"/accounts/{test_account.id}/history", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

def test_get_account_history_not_found(client, test_user_token):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    response = client.get("/accounts/999999/history", headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_get_account_receipts(client, test_user_token, test_account):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    response = client.get(f"/accounts/{test_account.id}/receipts", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

def test_get_account_receipts_not_found(client, test_user_token):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    response = client.get("/accounts/999999/receipts", headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_generate_receipt(client, test_user_token, test_account):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    response = client.post(f"/accounts/{test_account.id}/receipts", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert "receipt_url" in response.json()
    assert "qr_code_url" in response.json()

def test_generate_receipt_not_found(client, test_user_token):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    response = client.post("/accounts/999999/receipts", headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND 