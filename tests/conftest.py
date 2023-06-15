
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest
from fastapi.testclient import TestClient
from src.db.database import Base, get_db
from src.main import app

TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24


@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture()
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@pytest.fixture
def test_user(client):
    user = {
        "email": "otisredding@gmail.com",
        "first_name": "Otis",
        "last_name": "Redding",
        "password": "secret",
        "password_confirmation": "secret",
    }
    res = client.post("/api/v1/users/register/", json=user)

    assert res.status_code == 201
    new_user = res.json()
    new_user["data"]["password"] = user.get("password")
    new_user["data"]["id"] = 1
    return new_user


@pytest.fixture
def authorized_user(client, test_user):
    res = client.post(
        "/api/v1/users/login",
        data={
            "username": test_user.get('data').get("email"),
            "password": test_user.get('data').get("password"),
        },
    )
    res_body = res.json()
    token = res_body.get("data").get("token")
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}

    return client, test_user