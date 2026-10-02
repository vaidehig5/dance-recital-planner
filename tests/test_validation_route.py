from io import BytesIO

from backend.app import create_app


def make_client():
    app = create_app()
    app.config.update(TESTING=True)
    return app.test_client()


def test_upload_of_valid_file_reports_no_problems():
    client = make_client()
    data = {"file": (BytesIO(b"Ballet,Jazz\nAlice,Maya\n"), "show.csv")}

    body = client.post("/api/upload", data=data).get_json()

    assert body["is_valid"] is True
    assert body["errors"] == []
    assert body["warnings"] == []


def test_upload_with_content_problems_returns_errors_but_still_status_200():
    client = make_client()
    data = {"file": (BytesIO(b"Ballet,\nAlice,Bob\n"), "show.csv")}

    response = client.post("/api/upload", data=data)
    body = response.get_json()

    assert response.status_code == 200
    assert body["is_valid"] is False
    assert body["errors"][0]["message"] == "Column 2 does not have a dance name in the first row."
    assert body["errors"][0]["column_number"] == 2
    assert len(body["columns"]) == 2