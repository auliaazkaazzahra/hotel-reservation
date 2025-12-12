"""
Global test fixtures untuk testing
"""
from datetime import date, timedelta
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from src.application.reservation_service import ReservationService
from src.infrastructure.auth.user_repository import UserRepository
from src.infrastructure.reservation_repository import ReservationRepository
from src.main import app


@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def reservation_repository():
    """Repository instance untuk testing"""
    repo = ReservationRepository()
    yield repo
    repo.clear()


@pytest.fixture
def user_repository():
    """User repository untuk testing"""
    repo = UserRepository()
    yield repo


@pytest.fixture
def reservation_service(reservation_repository):
    """Service instance dengan repository"""
    return ReservationService(reservation_repository)


@pytest.fixture
def sample_customer_id():
    """Sample customer ID"""
    return "CUST-TEST-001"


@pytest.fixture
def sample_stay_period():
    """Sample stay period (3 nights)"""
    return {"check_in": date.today() + timedelta(days=7), "check_out": date.today() + timedelta(days=10)}


@pytest.fixture
def sample_room_details():
    """Sample room details"""
    return [{"room_id": "ROOM-001", "room_type": "Deluxe", "number_of_guests": 2, "price_per_night": Decimal("500000")}]


@pytest.fixture
def sample_reservation_data(sample_customer_id, sample_stay_period, sample_room_details):
    """Complete reservation data"""
    return {
        "customer_id": sample_customer_id,
        "check_in_date": sample_stay_period["check_in"],
        "check_out_date": sample_stay_period["check_out"],
        "room_details": sample_room_details,
    }


@pytest.fixture
def auth_headers(client):
    """Get authentication token untuk testing"""
    # Login dengan default user
    response = client.post("/api/auth/login", data={"username": "admin", "password": "admin123"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
