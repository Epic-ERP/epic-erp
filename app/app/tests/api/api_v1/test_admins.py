from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud
from app.core.config import settings
from app.schemas.users.user import UserCreate
from app.tests.utils.utils import random_email, random_lower_string


def test_get_existing_admin(client: TestClient, superuser_token_headers: dict, db: Session) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/admins/",
        headers=superuser_token_headers,
    )
    assert 200 <= r.status_code < 300
    api_user = r.json()
    existing_user = crud.admin.get(db, id=1)
    assert existing_user
    assert existing_user.user_id == api_user["user_id"]
    assert existing_user.permissions == api_user["permissions"]


def test_create_admin_existing_id(client: TestClient, superuser_token_headers: dict, db: Session) -> None:
    username = random_email()
    # username = email
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password, type="admin")
    admin_id = crud.user.create(db, obj_in=user_in).id
    data = {"user_id": admin_id, "permissions": 0}
    r = client.post(
        f"{settings.API_V1_STR}/admins/",
        headers=superuser_token_headers,
        json=data,
    )
    created_user = r.json()
    assert r.status_code == 400
    assert "user_id" not in created_user


def test_update_admin(client: TestClient, superuser_token_headers: dict, db: Session) -> None:
    username = random_email()
    # username = email
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password, type="admin")
    admin_id = crud.user.create(db, obj_in=user_in).id
    data = {"user_id": admin_id, "permissions": 5}
    r = client.put(
        f"{settings.API_V1_STR}/admins/",
        headers=superuser_token_headers,
        json=data,
    )
    updated_admin = r.json()
    assert 200 <= r.status_code < 300
    assert updated_admin["permissions"] == 5


def test_create_admin_existing_nonadmin(client: TestClient, superuser_token_headers: dict, db: Session) -> None:
    username = random_email()
    # username = email
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password, type="professor")
    user = crud.user.create(db, obj_in=user_in)
    admin_id = user.id
    data = {"user_id": admin_id, "permissions": 0}
    r = client.post(
        f"{settings.API_V1_STR}/admins/",
        headers=superuser_token_headers,
        json=data,
    )
    created_admin = r.json()
    db.refresh(user)
    assert 200 <= r.status_code < 300
    assert user
    assert user.is_admin
    assert "user_id" in created_admin
    assert "permissions" in created_admin
