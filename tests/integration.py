import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.future import select
import asyncio

# ---- Import your app and DB definitions ----
from app.app import app
from app.db import Base, get_async_session, User


# --------------------------------------------------------------------------
# TEST DATABASE SETUP
# --------------------------------------------------------------------------

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create an asyncio event loop for the TestClient context."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_engine():
    """Create an async in-memory SQLite engine and tables."""
    engine = create_async_engine(TEST_DATABASE_URL)
    async def create_all():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    asyncio.run(create_all())
    yield engine
    asyncio.run(engine.dispose())


@pytest.fixture
def test_session(test_engine):
    """Provide an AsyncSession instance for overrides."""
    async_session = async_sessionmaker(test_engine, expire_on_commit=False)

    async def get_session():
        async with async_session() as session:
            yield session

    return get_session


@pytest.fixture(autouse=True)
def override_dependency(test_session):
    """Override DB dependency inside FastAPI app itself."""
    # Define a dependency override function that yields sessions from test DB
    async def override_get_async_session():
        async for s in test_session():
            yield s

    # Actually override inside FastAPI
    app.dependency_overrides[get_async_session] = override_get_async_session
    yield
    app.dependency_overrides.clear()

@pytest.fixture
def client():
    """FastAPI synchronous test client."""
    with TestClient(app) as c:
        yield c


# --------------------------------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------------------------------

def register_user(client: TestClient, email: str, password: str):
    res = client.post("/auth/register", json={
        "email": email,
        "password": password,
        "is_active": True,
        "is_superuser": False,
        "is_verified": False
    })
    assert res.status_code == 201, res.text
    return res.json()


def login_user(client: TestClient, email: str, password: str):
    res = client.post("/auth/jwt/login", data={"username": email, "password": password})
    assert res.status_code == 200, res.text
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# --------------------------------------------------------------------------
# LOCAL SUPERUSER PROMOTION (TEST-ONLY)
# --------------------------------------------------------------------------

def promote_user_in_test_db(email: str, session_generator):
    """Directly promote user to superuser using test DB session."""
    async def _promote():
        async for session in session_generator():
            result = await session.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()
            if not user:
                raise ValueError(f"User {email} not found in test DB")
            user.is_superuser = True
            session.add(user)
            await session.commit()
            break
    asyncio.run(_promote())


# --------------------------------------------------------------------------
# INTEGRATION TEST
# --------------------------------------------------------------------------

def test_full_flow(client, test_session):
    """
    Complete synchronous integration test using TestClient.
    """

    # Register users
    register_user(client, "admin@example.com", "adminpass")
    register_user(client, "user@example.com", "userpass")

    # Promote admin to superuser (using in-memory DB)
    promote_user_in_test_db("admin@example.com", test_session)

    # Login both users
    admin_headers = login_user(client, "admin@example.com", "adminpass")
    user_headers = login_user(client, "user@example.com", "userpass")

    # Assert admin promotion 
    res = client.get("/users/me/", headers=admin_headers)
    assert res.status_code == 200, res.text
    assert res.json()["is_superuser"] is True, res.text

    # Create a room (admin)
    room_payload = {"name": "Main Conference Room", "capacity": 10}
    res = client.post("/rooms/", json=room_payload, headers=admin_headers)
    assert res.status_code == 201, res.text
    room_id = res.json()["id"]

    # Normal user cannot create room
    res = client.post("/rooms/", json={"name": "Unauthorized", "capacity": 5}, headers=user_headers)
    assert res.status_code == 403

    # Admin can update room
    res = client.put(f"/rooms/{room_id}", json={ "name": "Dummy", "capacity": 50}, headers=admin_headers)
    assert res.status_code == 200

    # Normal users cannot update room
    res = client.put(f"/rooms/{room_id}", json={ "name": "Dummy2", "capacity": 30}, headers=user_headers)
    assert res.status_code == 403

    room_payload2 = {"name": "Scrum meeting", "capacity": 4}
    res2 = client.post("/rooms/", json=room_payload2, headers=admin_headers)
    assert res2.status_code == 201, res2.text
    room_id2 = res2.json()["id"]

    # Admin Delete room
    res = client.delete(f"/rooms/{room_id2}", headers=admin_headers)
    assert res.status_code == 204

    room_payload3 = {"name": "Scrum meeting 2", "capacity": 4}
    res3 = client.post("/rooms/", json=room_payload3, headers=admin_headers)
    assert res3.status_code == 201, res3.text
    room_id3 = res3.json()["id"]

    # user delete room (should fail)
    res = client.delete(f"/rooms/{room_id3}", headers=user_headers)
    assert res.status_code == 403

    # List rooms
    res = client.get("/rooms/", headers=user_headers)
    assert res.status_code == 200
    assert len(res.json()) > 0

    # Create a booking
    start = datetime.now(timezone.utc) + timedelta(hours=1)
    end = start + timedelta(hours=2)
    booking_payload = {
        "room_id": room_id,
        "start_time": start.isoformat(),
        "end_time": end.isoformat(),
        "purpose": "Team Discussion",
    }
    res = client.post("/bookings/", json=booking_payload, headers=user_headers)
    assert res.status_code == 200, res.text
    booking_id = res.json()["id"]

    # Create a booking with more than 4hrs duration
    start = datetime.now(timezone.utc) + timedelta(hours=3)
    end = start + timedelta(hours=5)
    booking_payload = {
        "room_id": room_id,
        "start_time": start.isoformat(),
        "end_time": end.isoformat(),
        "purpose": "Team Discussion",
    }
    res = client.post("/bookings/", json=booking_payload, headers=user_headers)
    assert res.status_code == 400
    assert "Exceeds the Max duration" in res.text

    # Invalid booking (start in past)
    past_start = datetime.now(timezone.utc) - timedelta(hours=1)
    past_end = past_start + timedelta(hours=2)
    invalid_booking = {
        "room_id": room_id,
        "start_time": past_start.isoformat(),
        "end_time": past_end.isoformat(),
        "purpose": "Invalid",
    }
    res = client.post("/bookings/", json=invalid_booking, headers=user_headers)
    assert res.status_code == 400
    assert "greater than current time" in res.text

    # Invalid Booking end time is less than start time
    start = datetime.now(timezone.utc) + timedelta(hours=1)
    past_end = past_start - timedelta(hours=2)
    invalid_booking = {
        "room_id": room_id,
        "start_time": start.isoformat(),
        "end_time": past_end.isoformat(),
        "purpose": "Invalid",
    }
    res = client.post("/bookings/", json=invalid_booking, headers=user_headers)
    assert res.status_code == 400
    assert "Start time must be before end time" in res.text

    # List bookings
    res = client.get("/bookings/", headers=user_headers)
    assert res.status_code == 200
    assert len(res.json()) >= 1

    #  Admin can delete user's booking 
    res = client.delete(f"/bookings/{booking_id}", headers=admin_headers)
    assert res.status_code == 204

    start = datetime.now(timezone.utc) + timedelta(hours=5)
    end = start + timedelta(hours=1)
    booking_payload = {
        "room_id": room_id,
        "start_time": start.isoformat(),
        "end_time": end.isoformat(),
        "purpose": "Team Discussion 2",
    }
    res = client.post("/bookings/", json=booking_payload, headers=admin_headers)
    assert res.status_code == 200, res.text
    booking_id = res.json()["id"]

    #  User can't delete other user's booking 
    res = client.delete(f"/bookings/{booking_id}", headers=user_headers)
    assert res.status_code == 403
