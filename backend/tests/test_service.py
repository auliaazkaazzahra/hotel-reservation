"""
Unit tests untuk ReservationService
Coverage: Use cases, business workflows, error handling
"""
from datetime import date, timedelta
from decimal import Decimal

import pytest

from src.domain.value_objects.value_objects import BookingStatus


class TestReservationService:
    """Test ReservationService use cases"""

    def test_create_reservation(self, reservation_service, sample_reservation_data):
        """Test: Create reservation use case"""
        reservation = reservation_service.create_reservation(
            customer_id=sample_reservation_data["customer_id"],
            check_in_date=sample_reservation_data["check_in_date"],
            check_out_date=sample_reservation_data["check_out_date"],
            room_details=sample_reservation_data["room_details"],
        )

        assert reservation.reservation_id is not None
        assert reservation.customer_id.value == sample_reservation_data["customer_id"]
        assert reservation.booking_status == BookingStatus.BOOKED
        assert len(reservation.reservation_details) == 1
        assert reservation.total_amount.amount > 0

    def test_create_reservation_invalid_dates(self, reservation_service):
        """Test: Create reservation dengan tanggal invalid"""
        with pytest.raises(ValueError):
            reservation_service.create_reservation(
                customer_id="CUST-001",
                check_in_date=date.today(),
                check_out_date=date.today() - timedelta(days=1),  # Invalid
                room_details=[
                    {
                        "room_id": "ROOM-001",
                        "room_type": "Deluxe",
                        "number_of_guests": 2,
                        "price_per_night": Decimal("500000"),
                    }
                ],
            )

    def test_create_reservation_empty_rooms(self, reservation_service, sample_stay_period):
        """Test: Create reservation tanpa kamar"""

        reservation = reservation_service.create_reservation(
            customer_id="CUST-001",
            check_in_date=sample_stay_period["check_in"],
            check_out_date=sample_stay_period["check_out"],
            room_details=[],
        )

        assert reservation is not None
        assert reservation.reservation_details == []
        assert reservation.total_amount is None or reservation.total_amount.amount == 0

    def test_get_reservation(self, reservation_service, sample_reservation_data):
        """Test: Get reservation by ID"""
        # Create first
        created = reservation_service.create_reservation(**sample_reservation_data)

        # Get
        retrieved = reservation_service.get_reservation(created.reservation_id)

        assert retrieved is not None
        assert retrieved.reservation_id == created.reservation_id
        assert retrieved.customer_id == created.customer_id

    def test_get_reservation_not_found(self, reservation_service):
        """Test: Get non-existent reservation"""
        result = reservation_service.get_reservation("non-existent-id")
        assert result is None

    def test_get_customer_reservations(self, reservation_service, sample_stay_period):
        """Test: Get all reservations for a customer"""
        customer_id = "CUST-MULTI-001"

        # Create multiple reservations
        for i in range(3):
            reservation_service.create_reservation(
                customer_id=customer_id,
                check_in_date=sample_stay_period["check_in"],
                check_out_date=sample_stay_period["check_out"],
                room_details=[
                    {
                        "room_id": f"ROOM-{i}",
                        "room_type": "Standard",
                        "number_of_guests": 1,
                        "price_per_night": Decimal("300000"),
                    }
                ],
            )

        # Get all
        reservations = reservation_service.get_customer_reservations(customer_id)

        assert len(reservations) == 3
        assert all(r.customer_id.value == customer_id for r in reservations)

    def test_get_customer_reservations_empty(self, reservation_service):
        """Test: Get reservations for customer with no reservations"""
        reservations = reservation_service.get_customer_reservations("CUST-NONE")
        assert len(reservations) == 0

    def test_add_room_to_reservation(self, reservation_service, sample_reservation_data):
        """Test: Add room to existing reservation"""
        # Create reservation
        reservation = reservation_service.create_reservation(**sample_reservation_data)
        initial_total = reservation.total_amount.amount

        # Add another room (sesuai signature kode Anda)
        updated = reservation_service.add_room_to_reservation(
            reservation_id=reservation.reservation_id,
            room_id="ROOM-002",
            room_type="Suite",
            number_of_guests=3,
            price_per_night=Decimal("800000"),
        )

        assert len(updated.reservation_details) == 2
        assert updated.total_amount.amount > initial_total

    def test_add_room_to_cancelled_reservation(self, reservation_service, sample_reservation_data):
        """Test: Cannot add room to cancelled reservation"""
        # Create and cancel
        reservation = reservation_service.create_reservation(**sample_reservation_data)
        reservation_service.cancel_reservation(reservation.reservation_id)

        # Try to add room
        with pytest.raises(ValueError, match="Cannot modify this reservation"):
            reservation_service.add_room_to_reservation(
                reservation_id=reservation.reservation_id,
                room_id="ROOM-002",
                room_type="Standard",
                number_of_guests=1,
                price_per_night=Decimal("300000"),
            )

    def test_confirm_payment(self, reservation_service, sample_reservation_data):
        """Test: Confirm payment use case"""
        reservation = reservation_service.create_reservation(**sample_reservation_data)

        updated = reservation_service.confirm_payment(
            reservation_id=reservation.reservation_id, payment_id="PAY-TEST-001"
        )

        assert updated.booking_status == BookingStatus.PAID
        assert updated.payment_id.value == "PAY-TEST-001"

    def test_confirm_payment_not_found(self, reservation_service):
        """Test: Confirm payment for non-existent reservation"""
        with pytest.raises(ValueError, match="not found"):
            reservation_service.confirm_payment(reservation_id="non-existent", payment_id="PAY-001")

    def test_confirm_reservation(self, reservation_service, sample_reservation_data):
        """Test: Confirm reservation use case"""
        # Create and pay
        reservation = reservation_service.create_reservation(**sample_reservation_data)
        reservation_service.confirm_payment(reservation.reservation_id, "PAY-001")

        # Confirm
        updated = reservation_service.confirm_reservation(reservation.reservation_id)

        assert updated.booking_status == BookingStatus.CONFIRMED

    def test_confirm_reservation_not_paid(self, reservation_service, sample_reservation_data):
        """Test: Cannot confirm unpaid reservation"""
        reservation = reservation_service.create_reservation(**sample_reservation_data)

        with pytest.raises(ValueError, match="must be paid before confirmation"):
            reservation_service.confirm_reservation(reservation.reservation_id)

    def test_cancel_reservation(self, reservation_service, sample_reservation_data):
        """Test: Cancel reservation use case"""
        reservation = reservation_service.create_reservation(**sample_reservation_data)

        updated = reservation_service.cancel_reservation(reservation.reservation_id)

        assert updated.booking_status == BookingStatus.CANCELLED

    def test_cancel_already_cancelled(self, reservation_service, sample_reservation_data):
        """Test: Cannot cancel confirmed reservation"""
        reservation = reservation_service.create_reservation(**sample_reservation_data)
        reservation_service.confirm_payment(reservation.reservation_id, "PAY-001")
        reservation_service.confirm_reservation(reservation.reservation_id)

        with pytest.raises(ValueError, match="Cannot cancel confirmed reservation"):
            reservation_service.cancel_reservation(reservation.reservation_id)

    def test_delete_reservation(self, reservation_service, sample_reservation_data):
        """Test: Delete reservation use case"""
        reservation = reservation_service.create_reservation(**sample_reservation_data)

        result = reservation_service.delete_reservation(reservation.reservation_id)

        assert result is True
        assert reservation_service.get_reservation(reservation.reservation_id) is None

    def test_delete_non_existent_reservation(self, reservation_service):
        """Test: Delete non-existent reservation"""
        result = reservation_service.delete_reservation("non-existent")
        assert result is False

    def test_complete_workflow(self, reservation_service, sample_reservation_data):
        """Test: Complete business workflow"""
        # 1. Create reservation
        reservation = reservation_service.create_reservation(**sample_reservation_data)
        assert reservation.booking_status == BookingStatus.BOOKED

        # 2. Add another room (sesuai signature)
        reservation = reservation_service.add_room_to_reservation(
            reservation_id=reservation.reservation_id,
            room_id="ROOM-002",
            room_type="Standard",
            number_of_guests=1,
            price_per_night=Decimal("300000"),
        )

        def test_add_room_to_non_existent_reservation(self, reservation_service):
            """Test: Add room to non-existent reservation"""
            with pytest.raises(ValueError, match="not found"):
                reservation_service.add_room_to_reservation(
                    reservation_id="non-existent",
                    room_id="ROOM-001",
                    room_type="Standard",
                    number_of_guests=1,
                    price_per_night=Decimal("300000"),
                )

        def test_confirm_reservation_not_found(self, reservation_service):
            """Test: Confirm non-existent reservation"""
            with pytest.raises(ValueError, match="not found"):
                reservation_service.confirm_reservation("non-existent")

        def test_cancel_reservation_not_found(self, reservation_service):
            """Test: Cancel non-existent reservation"""
            with pytest.raises(ValueError, match="not found"):
                reservation_service.cancel_reservation("non-existent")

        # 3. Confirm payment
        reservation = reservation_service.confirm_payment(
            reservation_id=reservation.reservation_id, payment_id="PAY-WORKFLOW-001"
        )
        assert reservation.booking_status == BookingStatus.PAID

        # 4. Confirm reservation
        reservation = reservation_service.confirm_reservation(reservation.reservation_id)
        assert reservation.booking_status == BookingStatus.CONFIRMED

        # 5. Verify final state
        final = reservation_service.get_reservation(reservation.reservation_id)
        assert final.booking_status == BookingStatus.CONFIRMED
        assert len(final.reservation_details) == 2
