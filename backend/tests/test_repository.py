"""
Unit tests untuk ReservationRepository
Coverage: Persistence operations
"""
from datetime import date, timedelta
from decimal import Decimal

import pytest

from src.domain.entities.reservation import Reservation
from src.domain.value_objects.value_objects import BookingStatus, CustomerID, StayPeriod


class TestReservationRepository:
    """Test ReservationRepository"""

    def test_save_reservation(self, reservation_repository):
        """Test: Save reservation to storage"""
        reservation = Reservation(
            customer_id=CustomerID(value="CUST-001"),
            stay_period=StayPeriod(
                check_in_date=date.today() + timedelta(days=1), check_out_date=date.today() + timedelta(days=3)
            ),
            booking_status=BookingStatus.BOOKED,
        )

        saved = reservation_repository.save(reservation)

        assert saved.reservation_id == reservation.reservation_id
        assert reservation_repository.find_by_id(saved.reservation_id) is not None

    def test_find_by_id_exists(self, reservation_repository):
        """Test: Find reservation by existing ID"""
        reservation = Reservation(
            customer_id=CustomerID(value="CUST-001"),
            stay_period=StayPeriod(
                check_in_date=date.today() + timedelta(days=1), check_out_date=date.today() + timedelta(days=3)
            ),
            booking_status=BookingStatus.BOOKED,
        )

        saved = reservation_repository.save(reservation)
        found = reservation_repository.find_by_id(saved.reservation_id)

        assert found is not None
        assert found.reservation_id == saved.reservation_id

    def test_find_by_id_not_exists(self, reservation_repository):
        """Test: Find non-existent reservation"""
        found = reservation_repository.find_by_id("non-existent-id")
        assert found is None

    def test_find_by_customer_id(self, reservation_repository):
        """Test: Find all reservations by customer ID"""
        customer_id = "CUST-MULTI"

        # Create 3 reservations for same customer
        for _ in range(3):
            reservation = Reservation(
                customer_id=CustomerID(value=customer_id),
                stay_period=StayPeriod(
                    check_in_date=date.today() + timedelta(days=1), check_out_date=date.today() + timedelta(days=3)
                ),
                booking_status=BookingStatus.BOOKED,
            )
            reservation_repository.save(reservation)

        # Create 1 reservation for different customer
        other = Reservation(
            customer_id=CustomerID(value="CUST-OTHER"),
            stay_period=StayPeriod(
                check_in_date=date.today() + timedelta(days=1), check_out_date=date.today() + timedelta(days=3)
            ),
            booking_status=BookingStatus.BOOKED,
        )
        reservation_repository.save(other)

        # Find by customer
        found = reservation_repository.find_by_customer_id(customer_id)

        assert len(found) == 3
        assert all(r.customer_id.value == customer_id for r in found)

    def test_find_all(self, reservation_repository):
        """Test: Find all reservations"""
        # Create 5 reservations
        for i in range(5):
            reservation = Reservation(
                customer_id=CustomerID(value=f"CUST-{i}"),
                stay_period=StayPeriod(
                    check_in_date=date.today() + timedelta(days=1), check_out_date=date.today() + timedelta(days=3)
                ),
                booking_status=BookingStatus.BOOKED,
            )
            reservation_repository.save(reservation)

        all_reservations = reservation_repository.find_all()
        assert len(all_reservations) == 5

    def test_delete_existing_reservation(self, reservation_repository):
        """Test: Delete existing reservation"""
        reservation = Reservation(
            customer_id=CustomerID(value="CUST-001"),
            stay_period=StayPeriod(
                check_in_date=date.today() + timedelta(days=1), check_out_date=date.today() + timedelta(days=3)
            ),
            booking_status=BookingStatus.BOOKED,
        )

        saved = reservation_repository.save(reservation)

        # Delete
        result = reservation_repository.delete(saved.reservation_id)

        assert result is True
        assert reservation_repository.find_by_id(saved.reservation_id) is None

    def test_delete_non_existing_reservation(self, reservation_repository):
        """Test: Delete non-existent reservation"""
        result = reservation_repository.delete("non-existent")
        assert result is False

    def test_clear_storage(self, reservation_repository):
        """Test: Clear all storage"""
        # Add some reservations
        for i in range(3):
            reservation = Reservation(
                customer_id=CustomerID(value=f"CUST-{i}"),
                stay_period=StayPeriod(
                    check_in_date=date.today() + timedelta(days=1), check_out_date=date.today() + timedelta(days=3)
                ),
                booking_status=BookingStatus.BOOKED,
            )
            reservation_repository.save(reservation)

        # Clear
        reservation_repository.clear()

        # Verify empty
        assert len(reservation_repository.find_all()) == 0

    def test_update_existing_reservation(self, reservation_repository):
        """Test: Update existing reservation"""
        reservation = Reservation(
            customer_id=CustomerID(value="CUST-001"),
            stay_period=StayPeriod(
                check_in_date=date.today() + timedelta(days=1), check_out_date=date.today() + timedelta(days=3)
            ),
            booking_status=BookingStatus.BOOKED,
        )

        saved = reservation_repository.save(reservation)

        # Update status
        saved.confirm_payment("PAY-001")

        # Save again (update)
        updated = reservation_repository.save(saved)

        # Verify update
        found = reservation_repository.find_by_id(saved.reservation_id)
        assert found.booking_status == BookingStatus.PAID
        assert found.payment_id.value == "PAY-001"
