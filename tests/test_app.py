from backend.app import create_app


def make_client():
    app = create_app()
    app.config.update(TESTING=True)
    return app.test_client()


def test_health_endpoint_returns_ok():
    client = make_client()
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "app": "dance-recital-planner"}


def test_home_page_loads():
    client = make_client()
    response = client.get("/")

    assert response.status_code == 200
    assert b"Dance Recital Planner" in response.data