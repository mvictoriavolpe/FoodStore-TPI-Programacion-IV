import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy import event

from app.main import app
from app.core import database
from app.db.seed import seed


@pytest.fixture()
def clients(tmp_path, monkeypatch):
    engine = create_engine(
        f'sqlite:///{(tmp_path / "test.db").as_posix()}',
        connect_args={"check_same_thread": False, "timeout": 30},
    )

    @event.listens_for(engine, "connect")
    def foreign_keys(connection, _):
        connection.execute("PRAGMA foreign_keys=ON")

    monkeypatch.setattr(database, "engine", engine)
    seed()
    with TestClient(app) as customer, TestClient(app) as admin, TestClient(
        app
    ) as other:
        for client, name in [(customer, "cliente"), (other, "otrouser")]:
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "username": name,
                    "full_name": name.title(),
                    "email": f"{name}@example.com",
                    "password": "Cliente123!",
                },
            )
            assert response.status_code == 201, response.text
            assert (
                client.post(
                    "/api/v1/auth/token",
                    data={"username": name, "password": "Cliente123!"},
                ).status_code
                == 200
            )
        assert (
            admin.post(
                "/api/v1/auth/token",
                data={"username": "admin", "password": "Admin1234!"},
            ).status_code
            == 200
        )
        yield customer, admin, other, engine
    engine.dispose()
