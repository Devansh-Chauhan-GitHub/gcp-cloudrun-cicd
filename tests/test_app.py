from unittest.mock import patch

from app import app


def test_root_endpoint():
    with patch("services.users.get_users") as mock_get_users:
        mock_get_users.return_value = []

        client = app.test_client()
        response = client.get("/")

        assert response.status_code == 200
        assert response.json == []
