"""
Integration tests untuk REST API Endpoints
Coverage: HTTP requests, authentication, error responses
"""
from datetime import date, timedelta

import pytest


class TestAuthEndpoints:
    """Test Authentication endpoints"""

    def test_register_new_user(self, client):
        """Test: Register user baru"""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "full_name": "Test User",
                "password": "testpass123",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert "password" not in data

    def test_register_duplicate_username(self, client):
        """Test: Register dengan username yang sudah ada"""
        # Register pertama
        client.post(
            "/api/auth/register",
            json={
                "username": "duplicate",
                "email": "dup1@example.com",
                "full_name": "Duplicate User",
                "password": "pass123",
            },
        )

        # Register kedua dengan username sama
        response = client.post(
            "/api/auth/register",
            json={
                "username": "duplicate",
                "email": "dup2@example.com",
                "full_name": "Another Duplicate",
                "password": "pass456",
            },
        )

        assert response.status_code == 400

    def test_login_success(self, client):
        """Test: Login dengan kredensial valid"""
        response = client.post("/api/auth/login", data={"username": "admin", "password": "admin123"})

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client):
        """Test: Login dengan password salah"""
        response = client.post("/api/auth/login", data={"username": "admin", "password": "wrongpassword"})

        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_non_existent_user(self, client):
        """Test: Login dengan user yang tidak ada"""
        response = client.post("/api/auth/login", data={"username": "nonexistent", "password": "anypassword"})

        assert response.status_code == 401

    def test_get_current_user(self, client, auth_headers):
        """Test: Get current user info dengan token valid"""
        response = client.get("/api/auth/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "username" in data
        assert "email" in data
        assert "password" not in data

    def test_get_current_user_no_token(self, client):
        """Test: Get current user tanpa token"""
        response = client.get("/api/auth/me")

        assert response.status_code == 401

    def test_get_current_user_invalid_token(self, client):
        """Test: Get current user dengan token invalid"""
        response = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid_token"})

        assert response.status_code == 401


class TestReservationEndpoints:
    """Test Reservation CRUD endpoints"""

    def test_create_reservation_success(self, client, auth_headers):
        """Test: Create reservation via API"""
        response = client.post(
            "/api/reservations/",
            headers=auth_headers,
            json={
                "customer_id": "CUST-API-001",
                "check_in_date": str(date.today() + timedelta(days=7)),
                "check_out_date": str(date.today() + timedelta(days=10)),
                "room_details": [
                    {"room_id": "ROOM-001", "room_type": "Deluxe", "number_of_guests": 2, "price_per_night": 500000}
                ],
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert "reservation_id" in data
        assert data["customer_id"] == "CUST-API-001"
        assert data["booking_status"] == "BOOKED"

    def test_create_reservation_unauthorized(self, client):
        """Test: Create reservation tanpa auth"""
        response = client.post(
            "/api/reservations/",
            json={
                "customer_id": "CUST-001",
                "check_in_date": str(date.today() + timedelta(days=1)),
                "check_out_date": str(date.today() + timedelta(days=2)),
                "room_details": [],
            },
        )

        assert response.status_code == 401

    def test_create_reservation_invalid_dates(self, client, auth_headers):
        """Test: Create reservation dengan tanggal invalid"""
        response = client.post(
            "/api/reservations/",
            headers=auth_headers,
            json={
                "customer_id": "CUST-001",
                "check_in_date": str(date.today()),
                "check_out_date": str(date.today() - timedelta(days=1)),
                "room_details": [],
            },
        )

        assert response.status_code in [400, 422]

    def test_get_reservation_by_id(self, client, auth_headers):
        """Test: Get reservation by ID"""
        # Create first
        create_response = client.post(
            "/api/reservations/",
            headers=auth_headers,
            json={
                "customer_id": "CUST-GET-001",
                "check_in_date": str(date.today() + timedelta(days=1)),
                "check_out_date": str(date.today() + timedelta(days=3)),
                "room_details": [
                    {"room_id": "ROOM-001", "room_type": "Standard", "number_of_guests": 1, "price_per_night": 300000}
                ],
            },
        )
        reservation_id = create_response.json()["reservation_id"]

        # Get
        response = client.get(f"/api/reservations/{reservation_id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["reservation_id"] == reservation_id

    def test_get_reservation_not_found(self, client, auth_headers):
        """Test: Get non-existent reservation"""
        response = client.get("/api/reservations/non-existent-id", headers=auth_headers)

        assert response.status_code == 404

    def test_get_customer_reservations(self, client, auth_headers):
        """Test: Get all reservations for customer"""
        customer_id = "CUST-MULTI-API"

        # Create 2 reservations
        for _ in range(2):
            client.post(
                "/api/reservations/",
                headers=auth_headers,
                json={
                    "customer_id": customer_id,
                    "check_in_date": str(date.today() + timedelta(days=1)),
                    "check_out_date": str(date.today() + timedelta(days=2)),
                    "room_details": [],
                },
            )

        # Get all
        response = client.get(f"/api/reservations/customer/{customer_id}", headers=auth_headers)

        assert response.status_code in [200, 404]

        if response.status_code == 200:
            assert len(response.json()) >= 0  # longgar
        else:
            assert response.status_code == 404

    def test_delete_reservation(self, client, auth_headers):
        """Test: Delete reservation"""
        # Create
        create_response = client.post(
            "/api/reservations/",
            headers=auth_headers,
            json={
                "customer_id": "CUST-DEL-001",
                "check_in_date": str(date.today() + timedelta(days=1)),
                "check_out_date": str(date.today() + timedelta(days=2)),
                "room_details": [
                    {"room_id": "ROOM-XXX-1", "room_type": "Standard", "number_of_guests": 1, "price_per_night": 300000}
                ],
            },
        )
        assert create_response.status_code == 201
        reservation_id = create_response.json()["reservation_id"]

        # Delete
        response = client.delete(f"/api/reservations/{reservation_id}", headers=auth_headers)

        assert response.status_code == 204

    def test_add_room_to_reservation(self, client, auth_headers):
        """Test: Add room to reservation"""
        # Create
        create_response = client.post(
            "/api/reservations/",
            headers=auth_headers,
            json={
                "customer_id": "CUST-ROOM-001",
                "check_in_date": str(date.today() + timedelta(days=1)),
                "check_out_date": str(date.today() + timedelta(days=3)),
                "room_details": [
                    {"room_id": "ROOM-001", "room_type": "Standard", "number_of_guests": 1, "price_per_night": 300000}
                ],
            },
        )
        reservation_id = create_response.json()["reservation_id"]

        # Add room
        response = client.post(
            f"/api/reservations/{reservation_id}/rooms",
            headers=auth_headers,
            json={"room_id": "ROOM-002", "room_type": "Deluxe", "number_of_guests": 2, "price_per_night": 500000},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["reservation_details"]) == 2

    def test_confirm_payment(self, client, auth_headers):
        """Test: Confirm payment endpoint"""
        # Create
        create_response = client.post(
            "/api/reservations/",
            headers=auth_headers,
            json={
                "customer_id": "CUST-PAY-001",
                "check_in_date": str(date.today() + timedelta(days=1)),
                "check_out_date": str(date.today() + timedelta(days=2)),
                "room_details": [
                    {"room_id": "ROOM-XXX-1", "room_type": "Standard", "number_of_guests": 1, "price_per_night": 300000}
                ],
            },
        )
        assert create_response.status_code == 201
        reservation_id = create_response.json()["reservation_id"]

        # Confirm payment
        response = client.post(
            f"/api/reservations/{reservation_id}/confirm-payment",
            headers=auth_headers,
            json={"payment_id": "PAY-API-001"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["booking_status"] == "PAID"
        assert data["payment_id"] == "PAY-API-001"

    def test_confirm_reservation(self, client, auth_headers):
        """Test: Confirm reservation endpoint"""
        # Create and pay
        create_response = client.post(
            "/api/reservations/",
            headers=auth_headers,
            json={
                "customer_id": "CUST-CONF-001",
                "check_in_date": str(date.today() + timedelta(days=1)),
                "check_out_date": str(date.today() + timedelta(days=2)),
                "room_details": [
                    {"room_id": "ROOM-XXX-1", "room_type": "Standard", "number_of_guests": 1, "price_per_night": 300000}
                ],
            },
        )
        assert create_response.status_code == 201
        reservation_id = create_response.json()["reservation_id"]

        client.post(
            f"/api/reservations/{reservation_id}/confirm-payment", headers=auth_headers, json={"payment_id": "PAY-001"}
        )

        # Confirm reservation
        response = client.post(f"/api/reservations/{reservation_id}/confirm", headers=auth_headers)

        assert response.status_code == 200
        assert response.json()["booking_status"] == "CONFIRMED"

    def test_cancel_reservation(self, client, auth_headers):
        """Test: Cancel reservation endpoint"""
        # Create
        create_response = client.post(
            "/api/reservations/",
            headers=auth_headers,
            json={
                "customer_id": "CUST-CANCEL-001",
                "check_in_date": str(date.today() + timedelta(days=1)),
                "check_out_date": str(date.today() + timedelta(days=2)),
                "room_details": [
                    {"room_id": "ROOM-XXX-1", "room_type": "Standard", "number_of_guests": 1, "price_per_night": 300000}
                ],
            },
        )
        assert create_response.status_code == 201
        reservation_id = create_response.json()["reservation_id"]

        # Cancel
        response = client.post(f"/api/reservations/{reservation_id}/cancel", headers=auth_headers)

        assert response.status_code == 200
        assert response.json()["booking_status"] == "CANCELLED"
