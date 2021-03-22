from random import randint
from typing import Dict

from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from app import crud
from app.core.config import settings
from app.tests.utils.school import create_random_school
from app.tests.utils.user import authentication_token_from_email, create_random_user
from app.tests.utils.utils import random_email, random_lower_string, to_json


def test_get_all_schools(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    school = create_random_school(db)
    r = client.get(f"{settings.API_V1_STR}/schools/", headers=superuser_token_headers)
    assert r.status_code == 200
    results = r.json()
    assert results
    assert results[-1] == to_json(school)


def test_create_school(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    name = random_lower_string()
    head = random_lower_string()
    data = {'name': name, 'head': head}
    r = client.post(f"{settings.API_V1_STR}/schools/", headers=superuser_token_headers, json=data)
    assert r.status_code == 200
    created_school = r.json()
    school = crud.school.get_by_name(db, name=name)
    assert school
    assert created_school['name'] == school.name == name
    assert created_school['head'] == school.head == head


def test_create_school_existing(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    school = create_random_school(db)
    data = {'name': school.name, 'head': school.head}
    r = client.post(f"{settings.API_V1_STR}/schools/", headers=superuser_token_headers, json=data)
    assert r.status_code == 409


def test_create_school_duplicate_head(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    school = create_random_school(db)
    data = {'name': random_lower_string(), 'head': school.head}
    r = client.post(f"{settings.API_V1_STR}/schools/", headers=superuser_token_headers, json=data)
    assert r.status_code == 409


def test_get_school_superuser(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    school = create_random_school(db)
    r = client.get(f"{settings.API_V1_STR}/schools/{school.id}", headers=superuser_token_headers)
    assert r.status_code == 200
    fetched_school = r.json()
    assert fetched_school
    assert fetched_school == to_json(school)


def test_get_non_existing_school_superuser(
    client: TestClient, superuser_token_headers: Dict[str, str], db: Session
) -> None:
    school_id = crud.school.get_multi(db)[-1].id + 1
    r = client.get(f"{settings.API_V1_STR}/schools/{school_id}", headers=superuser_token_headers)
    assert r.status_code == 404


def test_get_school_admin(client: TestClient, db: Session) -> None:
    school = create_random_school(db)
    admin = create_random_user(db, "admin", permissions=4)
    admin_user_token_headers = authentication_token_from_email(
        client=client, db=db, email=admin.email, user_type="admin"
    )
    r = client.get(f"{settings.API_V1_STR}/schools/{school.id}", headers=admin_user_token_headers)
    assert r.status_code == 200
    fetched_school = r.json()
    assert fetched_school
    assert fetched_school == to_json(school)


def test_get_school_valid_student(client: TestClient, db: Session) -> None:
    school = create_random_school(db)
    admin_user_token_headers = authentication_token_from_email(
        client=client, db=db, email=random_email(), school_id=school.id
    )
    r = client.get(f"{settings.API_V1_STR}/schools/{school.id}", headers=admin_user_token_headers)
    assert r.status_code == 200
    fetched_school = r.json()
    assert fetched_school
    assert fetched_school == to_json(school)


def test_get_school_invalid_student(client: TestClient, db: Session) -> None:
    school = create_random_school(db)
    admin_user_token_headers = authentication_token_from_email(client=client, db=db, email=random_email())
    r = client.get(f"{settings.API_V1_STR}/schools/{school.id}", headers=admin_user_token_headers)
    assert r.status_code == 403


def test_update_school(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    school = create_random_school(db)
    new_name = random_lower_string()
    data = {'name': new_name, 'head': school.head}
    r = client.put(f"{settings.API_V1_STR}/schools/{school.id}", headers=superuser_token_headers, json=data)
    assert r.status_code == 200
    fetched_school = r.json()
    db.refresh(school)
    assert fetched_school
    assert fetched_school['id'] == school.id
    assert fetched_school['name'] == school.name == new_name
    assert fetched_school['head'] == school.head


def test_update_school_nonexisting(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    while crud.school.get(db, id=(school_id := randint(0, 10000000))):
        pass
    data = {'name': random_lower_string(), 'head': random_lower_string()}
    r = client.put(f"{settings.API_V1_STR}/schools/{school_id}", headers=superuser_token_headers, json=data)
    assert r.status_code == 404


def test_get_all_students(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    school = create_random_school(db)
    school_student = create_random_user(db=db, type="student", school_id=school.id)
    r = client.get(f"{settings.API_V1_STR}/schools/{school.id}/students", headers=superuser_token_headers)
    assert r.status_code == 200
    fetched_students = r.json()
    assert fetched_students
    assert fetched_students[0] == {
        key: value for key, value in to_json(school_student).items() if key in fetched_students[0].keys()
    }


def test_get_all_professors(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    school = create_random_school(db)
    school_student = create_random_user(db=db, type="professor", school_id=school.id)
    r = client.get(f"{settings.API_V1_STR}/schools/{school.id}/professors", headers=superuser_token_headers)
    assert r.status_code == 200
    fetched_students = r.json()
    assert fetched_students
    assert fetched_students[0] == {
        key: value for key, value in to_json(school_student).items() if key in fetched_students[0].keys()
    }


def test_delete_school(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    school = create_random_school(db)
    r = client.delete(f"{settings.API_V1_STR}/schools/{school.id}", headers=superuser_token_headers)
    assert r.status_code == 200
    deleted_school = crud.school.get(db, school.id)
    assert deleted_school is None


def test_delete_school_nonexisting(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    last_school_id = crud.school.get_multi(db)[-1].id
    r = client.delete(f"{settings.API_V1_STR}/schools/{last_school_id + 1}", headers=superuser_token_headers)
    assert r.status_code == 404
