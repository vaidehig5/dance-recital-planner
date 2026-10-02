from io import BytesIO

from backend.app import create_app


def make_client():
    app = create_app()
    app.config.update(TESTING=True)
    return app.test_client()


def test_upload_csv_returns_parsed_columns():
    client = make_client()
    data = {"file": (BytesIO(b"Ballet,Jazz\nAlice,Maya\n"), "show.csv")}

    response = client.post("/api/upload", data=data)

    assert response.status_code == 200
    assert response.get_json()["columns"][0] == {
        "column_number": 1,
        "dance_name": "Ballet",
        "dancers": ["Alice"],
    }


def test_upload_without_a_file_returns_friendly_error():
    client = make_client()

    response = client.post("/api/upload")

    assert response.status_code == 400
    assert "No file" in response.get_json()["error"]


def test_upload_of_unsupported_file_type_returns_friendly_error():
    client = make_client()
    data = {"file": (BytesIO(b"hello"), "notes.txt")}

    response = client.post("/api/upload", data=data)

    assert response.status_code == 400
    assert "supported" in response.get_json()["error"]