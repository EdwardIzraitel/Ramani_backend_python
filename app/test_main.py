from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_read_ping():
    response = client.get("/api/ping")
    assert response.status_code == 200
    assert response.json() == {"success": True}


def test_bad_tag():
    response = client.get("/api/posts", params={"tag": ""})
    assert response.status_code == 400
    assert response.json() == {"detail": "Tags parameter is required"}


def test_bad_sortBy():
    response = client.get("/api/posts", params={"tag": "tech", "sortBy": "2"})
    assert response.status_code == 400
    assert response.json() == {"detail": "sortBy parameter is invalid"}


def test_bad_direction():
    response = client.get(
        "/api/posts", params={"tag": "tech", "direction": "2"})
    assert response.status_code == 400
    assert response.json() == {"detail": "direction parameter is invalid"}


def test_goodSortBy_badDirection():
    response = client.get(
        "/api/posts", params={"tag": "tech", "sortBy": "reads", "direction": "2"})
    assert response.status_code == 400
    assert response.json() == {"detail": "direction parameter is invalid"}


def test_badSortBy_goodDirection():
    response = client.get(
        "/api/posts", params={"tag": "tech", "sortBy": "readss", "direction": "desc"})
    assert response.status_code == 400
    assert response.json() == {"detail": "sortBy parameter is invalid"}


def test_badTag_goodEverythingElse():
    response = client.get(
        "/api/posts", params={"tag": "", "sortBy": "readss", "direction": "desc"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Tags parameter is required"}


def test_single_tag():
    response = client.get(
        "/api/posts", params={"tag": "tech", "sortBy": "readss", "direction": "desc"})
    url = 'https://api.hatchways.io/assessment/blog/posts?tag='+"tech"
    assert response.status_code == 400
    assert response.json() == {"detail": "Tags parameter is required"}
