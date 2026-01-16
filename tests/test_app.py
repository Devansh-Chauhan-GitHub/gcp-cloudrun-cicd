from app import app


def test_root_endpoint():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"Hello from GCP Cloud Run" in response.data
