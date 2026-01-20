from unittest.mock import patch

from app import app


def test_root_endpoint_returns_html():
    with patch("services.users.get_users") as mock_get_users:
        mock_get_users.return_value = []

        client = app.test_client()
        response = client.get("/")

        assert response.status_code == 200
        assert response.content_type.startswith("text/html")


def test_api_users_endpoint_returns_json():
    with patch("services.users.get_users") as mock_get_users:
        mock_get_users.return_value = []

        client = app.test_client()
        response = client.get("/api/users")

        assert response.status_code == 200
        assert response.json == []
