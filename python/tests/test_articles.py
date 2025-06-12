import pytest
from fastapi import status
from datetime import datetime, timedelta

def test_get_articles(client):
    response = client.get("/articles")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

def test_get_article_by_id(client, test_article):
    response = client.get(f"/articles/{test_article.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == test_article.id
    assert response.json()["title"] == test_article.title
    assert response.json()["content"] == test_article.content

def test_get_article_not_found(client):
    response = client.get("/articles/999999")
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_create_article(client, test_admin_token, test_article_data):
    headers = {"Authorization": f"Bearer {test_admin_token}"}
    response = client.post("/articles", json=test_article_data, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    assert "id" in response.json()
    assert response.json()["title"] == test_article_data["title"]
    assert response.json()["content"] == test_article_data["content"]

def test_create_article_unauthorized(client, test_article_data):
    response = client.post("/articles", json=test_article_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_create_article_non_admin(client, test_user_token, test_article_data):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    response = client.post("/articles", json=test_article_data, headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_update_article(client, test_admin_token, test_article):
    headers = {"Authorization": f"Bearer {test_admin_token}"}
    update_data = {
        "title": "Updated Title",
        "content": "Updated content"
    }
    response = client.put(f"/articles/{test_article.id}", json=update_data, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == update_data["title"]
    assert response.json()["content"] == update_data["content"]

def test_update_article_unauthorized(client, test_article):
    update_data = {"title": "Updated Title"}
    response = client.put(f"/articles/{test_article.id}", json=update_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_update_article_non_admin(client, test_user_token, test_article):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    update_data = {"title": "Updated Title"}
    response = client.put(f"/articles/{test_article.id}", json=update_data, headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_update_article_not_found(client, test_admin_token):
    headers = {"Authorization": f"Bearer {test_admin_token}"}
    update_data = {"title": "Updated Title"}
    response = client.put("/articles/999999", json=update_data, headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_delete_article(client, test_admin_token, test_article):
    headers = {"Authorization": f"Bearer {test_admin_token}"}
    response = client.delete(f"/articles/{test_article.id}", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert "deleted" in response.json()["message"].lower()

def test_delete_article_unauthorized(client, test_article):
    response = client.delete(f"/articles/{test_article.id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_delete_article_non_admin(client, test_user_token, test_article):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    response = client.delete(f"/articles/{test_article.id}", headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_delete_article_not_found(client, test_admin_token):
    headers = {"Authorization": f"Bearer {test_admin_token}"}
    response = client.delete("/articles/999999", headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_search_articles(client):
    response = client.get("/articles/search?query=test")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

def test_get_articles_by_category(client):
    response = client.get("/articles/category/news")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

def test_get_articles_by_category_not_found(client):
    response = client.get("/articles/category/invalid_category")
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_get_articles_by_tag(client):
    response = client.get("/articles/tag/important")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

def test_get_articles_by_tag_not_found(client):
    response = client.get("/articles/tag/invalid_tag")
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_get_article_comments(client, test_article):
    response = client.get(f"/articles/{test_article.id}/comments")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

def test_add_article_comment(client, test_user_token, test_article):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    comment_data = {"content": "Test comment"}
    response = client.post(f"/articles/{test_article.id}/comments", json=comment_data, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    assert "id" in response.json()
    assert response.json()["content"] == comment_data["content"]

def test_add_article_comment_unauthorized(client, test_article):
    comment_data = {"content": "Test comment"}
    response = client.post(f"/articles/{test_article.id}/comments", json=comment_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_add_article_comment_not_found(client, test_user_token):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    comment_data = {"content": "Test comment"}
    response = client.post("/articles/999999/comments", json=comment_data, headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND 