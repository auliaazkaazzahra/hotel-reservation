"""
Extended API tests untuk mencapai 95% coverage
Coverage: Edge cases, error handling, bulk operations
"""
from datetime import date, timedelta

import pytest


class TestReservationEdgeCases:
    """Test edge cases untuk reservation API"""

    def test_create_reservation_with_many_rooms(self, client, auth_headers):
        """Test: Create reservation with 10 rooms"""
        rooms = [
            {"room_id": f"ROOM-BULK-{i}", "room_type": "Standard", "number_of_guests": 1, "price_per_night": 300000}
            for i in range(10)
        ]

        response = client.post(
            "/api/reservations/",
            headers=auth_headers,
            json={
                "customer_id": "CUST-BULK-001",
                "check_in_date": str(date.today() + timedelta(days=1)),
                "check_out_date": str(date.today() + timedelta(days=2)),
                "room_details": rooms,
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert len(data["reservation_details"]) == 10

    def test_create_reservation_single_room(self, client, auth_headers):
        """Test: Create reservation with exactly 1 room"""
        response = client.post(
            "/api/reservations/",
            headers=auth_headers,
            json={
                "customer_id": "CUST-SINGLE",
                "check_in_date": str(date.today() + timedelta(days=1)),
                "check_out_date": str(date.today() + timedelta(days=2)),
                "room_details": [
                    {"room_id": "ROOM-SINGLE", "room_type": "Deluxe", "number_of_guests": 2, "price_per_night": 500000}
                ],
            },
        )

        assert response.status_code == 201
        assert len(response.json()["reservation_details"]) == 1

    def test_malformed_json_request(self, client, auth_headers):
        """Test: Malformed JSON returns 422"""
        # Create custom headers with correct content type
        custom_headers = {**auth_headers}
        custom_headers["Content-Type"] = "application/json"

        response = client.post("/api/reservations/", headers=custom_headers, data="{invalid: json content}")

        assert response.status_code == 422

    def test_missing_required_fields(self, client, auth_headers):
        """Test: Missing required fields returns 422"""
        response = client.post(
            "/api/reservations/",
            headers=auth_headers,
            json={
                "customer_id": "CUST-001",
                # Missing check_in_date, check_out_date, room_details
            },
        )

        assert response.status_code == 422

    def test_invalid_date_format(self, client, auth_headers):
        """Test: Invalid date format returns error"""
        response = client.post(
            "/api/reservations/",
            headers=auth_headers,
            json={
                "customer_id": "CUST-001",
                "check_in_date": "invalid-date",
                "check_out_date": "also-invalid",
                "room_details": [],
            },
        )

        assert response.status_code == 422

    def test_negative_price_per_night(self, client, auth_headers):
        """Test: Negative price returns error"""
        response = client.post(
            "/api/reservations/",
            headers=auth_headers,
            json={
                "customer_id": "CUST-001",
                "check_in_date": str(date.today() + timedelta(days=1)),
                "check_out_date": str(date.today() + timedelta(days=2)),
                "room_details": [
                    {
                        "room_id": "ROOM-001",
                        "room_type": "Standard",
                        "number_of_guests": 1,
                        "price_per_night": -100000,  # Negative
                    }
                ],
            },
        )

        assert response.status_code in [400, 422]

    def test_zero_guests(self, client, auth_headers):
        """Test: Zero guests returns error"""
        response = client.post(
            "/api/reservations/",
            headers=auth_headers,
            json={
                "customer_id": "CUST-001",
                "check_in_date": str(date.today() + timedelta(days=1)),
                "check_out_date": str(date.today() + timedelta(days=2)),
                "room_details": [
                    {
                        "room_id": "ROOM-001",
                        "room_type": "Standard",
                        "number_of_guests": 0,  # Zero guests
                        "price_per_night": 300000,
                    }
                ],
            },
        )

        assert response.status_code in [400, 422]


class TestReservationErrorHandling:
    """Test error handling scenarios"""

    def test_get_reservation_invalid_id_format(self, client, auth_headers):
        """Test: Get reservation with invalid ID format"""
        response = client.get("/api/reservations/!@#$%^&*()", headers=auth_headers)

        assert response.status_code == 404

    def test_delete_non_existent_reservation(self, client, auth_headers):
        """Test: Delete non-existent reservation"""
        response = client.delete("/api/reservations/NON-EXISTENT-ID", headers=auth_headers)

        assert response.status_code == 404

    def test_add_room_to_non_existent_reservation(self, client, auth_headers):
        """Test: Add room to non-existent reservation"""
        response = client.post(
            "/api/reservations/NON-EXISTENT/rooms",
            headers=auth_headers,
            json={"room_id": "ROOM-001", "room_type": "Standard", "number_of_guests": 1, "price_per_night": 300000},
        )

        assert response.status_code in [400, 404]

    def test_confirm_payment_non_existent(self, client, auth_headers):
        """Test: Confirm payment for non-existent reservation"""
        response = client.post(
            "/api/reservations/NON-EXISTENT/confirm-payment", headers=auth_headers, json={"payment_id": "PAY-001"}
        )

        assert response.status_code in [400, 404]

    def test_confirm_reservation_non_existent(self, client, auth_headers):
        """Test: Confirm non-existent reservation"""
        response = client.post("/api/reservations/NON-EXISTENT/confirm", headers=auth_headers)

        assert response.status_code in [400, 404]

    def test_cancel_non_existent_reservation(self, client, auth_headers):
        """Test: Cancel non-existent reservation"""
        response = client.post("/api/reservations/NON-EXISTENT/cancel", headers=auth_headers)

        assert response.status_code in [400, 404]


class TestReservationWorkflows:
    """Test complex workflows"""

    def test_full_modification_workflow(self, client, auth_headers):
        """Test: Create -> Add Room -> Update -> Confirm -> Pay"""
        # 1. Create
        create_response = client.post(
            "/api/reservations/",
            headers=auth_headers,
            json={
                "customer_id": "CUST-WORKFLOW",
                "check_in_date": str(date.today() + timedelta(days=5)),
                "check_out_date": str(date.today() + timedelta(days=7)),
                "room_details": [
                    {"room_id": "ROOM-W1", "room_type": "Standard", "number_of_guests": 1, "price_per_night": 300000}
                ],
            },
        )

        assert create_response.status_code == 201
        reservation_id = create_response.json()["reservation_id"]

        # 2. Add another room
        add_response = client.post(
            f"/api/reservations/{reservation_id}/rooms",
            headers=auth_headers,
            json={"room_id": "ROOM-W2", "room_type": "Deluxe", "number_of_guests": 2, "price_per_night": 500000},
        )

        assert add_response.status_code == 200
        assert len(add_response.json()["reservation_details"]) == 2

        # 3. Confirm payment
        payment_response = client.post(
            f"/api/reservations/{reservation_id}/confirm-payment",
            headers=auth_headers,
            json={"payment_id": "PAY-WORKFLOW-001"},
        )

        assert payment_response.status_code == 200
        assert payment_response.json()["booking_status"] == "PAID"

        # 4. Confirm reservation
        confirm_response = client.post(f"/api/reservations/{reservation_id}/confirm", headers=auth_headers)

        assert confirm_response.status_code == 200
        assert confirm_response.json()["booking_status"] == "CONFIRMED"

    def test_cannot_modify_after_confirmation(self, client, auth_headers):
        """Test: Cannot add room after confirmation"""
        # Create and confirm
        create_response = client.post(
            "/api/reservations/",
            headers=auth_headers,
            json={
                "customer_id": "CUST-LOCKED",
                "check_in_date": str(date.today() + timedelta(days=1)),
                "check_out_date": str(date.today() + timedelta(days=2)),
                "room_details": [
                    {"room_id": "ROOM-L1", "room_type": "Standard", "number_of_guests": 1, "price_per_night": 300000}
                ],
            },
        )

        reservation_id = create_response.json()["reservation_id"]

        # Pay and confirm
        client.post(
            f"/api/reservations/{reservation_id}/confirm-payment", headers=auth_headers, json={"payment_id": "PAY-001"}
        )

        client.post(f"/api/reservations/{reservation_id}/confirm", headers=auth_headers)

        # Try to add room (should fail)
        add_response = client.post(
            f"/api/reservations/{reservation_id}/rooms",
            headers=auth_headers,
            json={"room_id": "ROOM-L2", "room_type": "Deluxe", "number_of_guests": 2, "price_per_night": 500000},
        )

        assert add_response.status_code == 400

    def test_multiple_customers_same_time(self, client, auth_headers):
        """Test: Multiple customers can book different rooms simultaneously"""
        customers = ["CUST-A", "CUST-B", "CUST-C"]
        reservations = []

        for i, customer_id in enumerate(customers):
            response = client.post(
                "/api/reservations/",
                headers=auth_headers,
                json={
                    "customer_id": customer_id,
                    "check_in_date": str(date.today() + timedelta(days=1)),
                    "check_out_date": str(date.today() + timedelta(days=2)),
                    "room_details": [
                        {
                            "room_id": f"ROOM-MULTI-{i}",
                            "room_type": "Standard",
                            "number_of_guests": 1,
                            "price_per_night": 300000,
                        }
                    ],
                },
            )

            assert response.status_code == 201
            reservations.append(response.json()["reservation_id"])

        # Verify all 3 reservations exist
        assert len(set(reservations)) == 3
