"""
Unit tests untuk Entities dan Aggregate Root
Coverage: Business logic, state transitions, validations
"""
from datetime import date, timedelta
from decimal import Decimal

import pytest

from src.domain.entities.reservation import Reservation
from src.domain.entities.reservation_detail import ReservationDetail
from src.domain.value_objects.value_objects import BookingStatus, CustomerID, PaymentID, RoomID, StayPeriod


class TestReservationDetail:
    """Test ReservationDetail Entity"""

    def test_create_valid_detail(self):
        """Test: Buat detail kamar valid"""
        detail = ReservationDetail(
            room_id=RoomID(value="ROOM-001"), room_type="Deluxe", number_of_guests=2, price_per_night=Decimal("500000")
        )

        assert detail.detail_id is not None
        assert detail.room_id.value == "ROOM-001"
        assert detail.room_type == "Deluxe"
        assert detail.number_of_guests == 2
        assert detail.price_per_night == Decimal("500000")

    def test_create_detail_without_room_id(self):
        """Test: Detail tanpa room_id harus error"""
        with pytest.raises(ValueError, match="RoomID is required"):
            ReservationDetail(room_id=None, room_type="Deluxe", number_of_guests=2, price_per_night=Decimal("500000"))

    def test_create_detail_zero_guests(self):
        """Test: Zero guests harus error"""
        with pytest.raises(ValueError, match="Number of guests must be at least 1"):
            ReservationDetail(
                room_id=RoomID(value="ROOM-001"),
                room_type="Standard",
                number_of_guests=0,
                price_per_night=Decimal("300000"),
            )

    def test_create_detail_negative_guests(self):
        """Test: Negative guests harus error"""
        with pytest.raises(ValueError, match="Number of guests must be at least 1"):
            ReservationDetail(
                room_id=RoomID(value="ROOM-001"),
                room_type="Standard",
                number_of_guests=-1,
                price_per_night=Decimal("300000"),
            )

    def test_create_detail_negative_price(self):
        """Test: Negative price harus error"""
        with pytest.raises(ValueError, match="Price per night cannot be negative"):
            ReservationDetail(
                room_id=RoomID(value="ROOM-001"),
                room_type="Standard",
                number_of_guests=1,
                price_per_night=Decimal("-100000"),
            )

    def test_calculate_subtotal(self):
        """Test: Kalkulasi subtotal"""
        detail = ReservationDetail(
            room_id=RoomID(value="ROOM-001"), room_type="Deluxe", number_of_guests=2, price_per_night=Decimal("500000")
        )

        subtotal = detail.calculate_subtotal(number_of_nights=3)
        assert subtotal == Decimal("1500000")

    def test_calculate_subtotal_one_night(self):
        """Test: Subtotal untuk 1 malam"""
        detail = ReservationDetail(
            room_id=RoomID(value="ROOM-001"), room_type="Deluxe", number_of_guests=2, price_per_night=Decimal("500000")
        )

        subtotal = detail.calculate_subtotal(number_of_nights=1)
        assert subtotal == Decimal("500000")

    def test_calculate_subtotal_zero_nights(self):
        """Test: Zero nights harus error"""
        detail = ReservationDetail(
            room_id=RoomID(value="ROOM-001"),
            room_type="Standard",
            number_of_guests=1,
            price_per_night=Decimal("300000"),
        )

        with pytest.raises(ValueError, match="Number of nights must be at least 1"):
            detail.calculate_subtotal(number_of_nights=0)

    def test_calculate_subtotal_negative_nights(self):
        """Test: Negative nights harus error"""
        detail = ReservationDetail(
            room_id=RoomID(value="ROOM-001"),
            room_type="Standard",
            number_of_guests=1,
            price_per_night=Decimal("300000"),
        )

        with pytest.raises(ValueError):
            detail.calculate_subtotal(number_of_nights=-1)

    def test_detail_unique_id(self):
        """Test: Setiap detail punya ID unik"""
        detail1 = ReservationDetail(
            room_id=RoomID(value="ROOM-001"), room_type="Deluxe", number_of_guests=2, price_per_night=Decimal("500000")
        )
        detail2 = ReservationDetail(
            room_id=RoomID(value="ROOM-002"), room_type="Suite", number_of_guests=3, price_per_night=Decimal("800000")
        )

        assert detail1.detail_id != detail2.detail_id

    def test_detail_equality(self):
        """Test: Equality berdasarkan detail_id"""
        detail1 = ReservationDetail(
            room_id=RoomID(value="ROOM-001"), room_type="Deluxe", number_of_guests=2, price_per_night=Decimal("500000")
        )

        assert detail1 == detail1

        detail2 = ReservationDetail(
            room_id=RoomID(value="ROOM-001"), room_type="Deluxe", number_of_guests=2, price_per_night=Decimal("500000")
        )

        assert detail1 != detail2  # Different IDs


class TestReservationAggregate:
    """Test Reservation Aggregate Root"""

    @pytest.fixture
    def basic_reservation(self):
        """Fixture: Basic reservation"""
        return Reservation(
            customer_id=CustomerID(value="CUST-001"),
            stay_period=StayPeriod(
                check_in_date=date.today() + timedelta(days=7), check_out_date=date.today() + timedelta(days=10)
            ),
            booking_status=BookingStatus.BOOKED,
        )

    def test_create_reservation(self, basic_reservation):
        """Test: Buat reservasi baru"""
        assert basic_reservation.reservation_id is not None
        assert basic_reservation.customer_id.value == "CUST-001"
        assert basic_reservation.booking_status == BookingStatus.BOOKED
        assert len(basic_reservation.reservation_details) == 0
        assert basic_reservation.created_at is not None
        assert basic_reservation.updated_at is not None

    def test_create_reservation_without_customer(self):
        """Test: Reservasi tanpa customer harus error"""
        with pytest.raises(ValueError, match="CustomerID is required"):
            Reservation(
                customer_id=None,
                stay_period=StayPeriod(
                    check_in_date=date.today() + timedelta(days=1), check_out_date=date.today() + timedelta(days=2)
                ),
                booking_status=BookingStatus.BOOKED,
            )

    def test_create_reservation_without_stay_period(self):
        """Test: Reservasi tanpa stay period harus error"""
        with pytest.raises(ValueError, match="StayPeriod is required"):
            Reservation(customer_id=CustomerID(value="CUST-001"), stay_period=None, booking_status=BookingStatus.BOOKED)

    def test_add_reservation_detail(self, basic_reservation):
        """Test: Tambah detail kamar"""
        detail = ReservationDetail(
            room_id=RoomID(value="ROOM-001"), room_type="Deluxe", number_of_guests=2, price_per_night=Decimal("500000")
        )

        basic_reservation.add_reservation_detail(detail)

        assert len(basic_reservation.reservation_details) == 1
        assert basic_reservation.reservation_details[0] == detail

    def test_add_invalid_detail_type(self, basic_reservation):
        """Test: Tambah detail dengan tipe salah harus error"""
        with pytest.raises(TypeError, match="Detail must be ReservationDetail instance"):
            basic_reservation.add_reservation_detail("invalid")

    def test_add_duplicate_room(self, basic_reservation):
        """Test: Cannot add same room twice"""
        detail = ReservationDetail(
            room_id=RoomID(value="ROOM-001"), room_type="Deluxe", number_of_guests=2, price_per_night=Decimal("500000")
        )

        basic_reservation.add_reservation_detail(detail)

        # Try to add same room again
        detail2 = ReservationDetail(
            room_id=RoomID(value="ROOM-001"),  # Same room
            room_type="Suite",
            number_of_guests=3,
            price_per_night=Decimal("800000"),
        )

        with pytest.raises(ValueError, match="already added to this reservation"):
            basic_reservation.add_reservation_detail(detail2)

    def test_remove_reservation_detail(self, basic_reservation):
        """Test: Remove detail kamar"""
        detail = ReservationDetail(
            room_id=RoomID(value="ROOM-001"), room_type="Deluxe", number_of_guests=2, price_per_night=Decimal("500000")
        )

        basic_reservation.add_reservation_detail(detail)
        assert len(basic_reservation.reservation_details) == 1

        # Remove
        basic_reservation.remove_reservation_detail(detail.detail_id)
        assert len(basic_reservation.reservation_details) == 0

    def test_remove_non_existing_detail(self, basic_reservation):
        """Test: Remove non-existent detail"""
        with pytest.raises(ValueError, match="not found"):
            basic_reservation.remove_reservation_detail("non-existent-id")

    def test_calculate_total_amount(self, basic_reservation):
        """Test: Kalkulasi total amount otomatis"""
        detail1 = ReservationDetail(
            room_id=RoomID(value="ROOM-001"), room_type="Deluxe", number_of_guests=2, price_per_night=Decimal("500000")
        )
        detail2 = ReservationDetail(
            room_id=RoomID(value="ROOM-002"), room_type="Suite", number_of_guests=3, price_per_night=Decimal("800000")
        )

        basic_reservation.add_reservation_detail(detail1)
        basic_reservation.add_reservation_detail(detail2)
        basic_reservation.calculate_total_amount()

        # 3 nights * (500000 + 800000) = 3,900,000
        expected_total = Decimal("3900000")
        assert basic_reservation.total_amount.amount == expected_total

    def test_calculate_total_amount_empty_details(self, basic_reservation):
        """Test: Total amount dengan no details = 0"""
        basic_reservation.calculate_total_amount()
        assert basic_reservation.total_amount.amount == Decimal("0")

    def test_confirm_payment(self, basic_reservation):
        """Test: State transition BOOKED -> PAID"""
        basic_reservation.confirm_payment(payment_id="PAY-001")

        assert basic_reservation.booking_status == BookingStatus.PAID
        assert basic_reservation.payment_id.value == "PAY-001"

    def test_confirm_payment_cancelled_reservation(self, basic_reservation):
        """Test: Confirm payment pada cancelled reservation harus error"""
        basic_reservation.booking_status = BookingStatus.CANCELLED

        with pytest.raises(ValueError, match="Cannot confirm payment for cancelled reservation"):
            basic_reservation.confirm_payment(payment_id="PAY-001")

    def test_confirm_reservation(self, basic_reservation):
        """Test: State transition PAID -> CONFIRMED"""
        basic_reservation.confirm_payment(payment_id="PAY-001")
        basic_reservation.confirm_reservation()

        assert basic_reservation.booking_status == BookingStatus.CONFIRMED

    def test_confirm_reservation_not_paid(self, basic_reservation):
        """Test: Confirm reservation sebelum bayar harus error"""
        with pytest.raises(ValueError, match="must be paid before confirmation"):
            basic_reservation.confirm_reservation()

    def test_cancel_reservation(self, basic_reservation):
        """Test: Cancel reservation"""
        basic_reservation.cancel_reservation()

        assert basic_reservation.booking_status == BookingStatus.CANCELLED

    def test_cancel_confirmed_reservation(self, basic_reservation):
        """Test: Cannot cancel confirmed reservation"""
        basic_reservation.confirm_payment(payment_id="PAY-001")
        basic_reservation.confirm_reservation()

        with pytest.raises(ValueError, match="Cannot cancel confirmed reservation"):
            basic_reservation.cancel_reservation()

    def test_is_modifiable_booked(self, basic_reservation):
        """Test: BOOKED status is modifiable"""
        assert basic_reservation.is_modifiable() is True

    def test_is_modifiable_paid(self, basic_reservation):
        """Test: PAID status is modifiable"""
        basic_reservation.confirm_payment("PAY-001")
        assert basic_reservation.is_modifiable() is True

    def test_is_modifiable_cancelled(self, basic_reservation):
        """Test: CANCELLED status is not modifiable"""
        basic_reservation.cancel_reservation()
        assert basic_reservation.is_modifiable() is False

    def test_is_modifiable_confirmed(self, basic_reservation):
        """Test: CONFIRMED status is not modifiable"""
        basic_reservation.confirm_payment("PAY-001")
        basic_reservation.confirm_reservation()
        assert basic_reservation.is_modifiable() is False

    def test_state_transition_workflow(self, basic_reservation):
        """Test: Complete workflow BOOKED -> PAID -> CONFIRMED"""
        # Initial state
        assert basic_reservation.booking_status == BookingStatus.BOOKED

        # Add room
        detail = ReservationDetail(
            room_id=RoomID(value="ROOM-001"), room_type="Deluxe", number_of_guests=2, price_per_night=Decimal("500000")
        )
        basic_reservation.add_reservation_detail(detail)

        # Confirm payment
        basic_reservation.confirm_payment(payment_id="PAY-001")
        assert basic_reservation.booking_status == BookingStatus.PAID

        # Confirm reservation
        basic_reservation.confirm_reservation()
        assert basic_reservation.booking_status == BookingStatus.CONFIRMED

    def test_updated_at_changes(self, basic_reservation):
        """Test: updated_at berubah saat modifikasi"""
        initial_update = basic_reservation.updated_at

        import time

        time.sleep(0.01)  # Small delay

        basic_reservation.confirm_payment(payment_id="PAY-001")
        assert basic_reservation.updated_at > initial_update

    def test_reservation_equality(self):
        """Test: Equality berdasarkan reservation_id"""
        reservation1 = Reservation(
            customer_id=CustomerID(value="CUST-001"),
            stay_period=StayPeriod(
                check_in_date=date.today() + timedelta(days=1), check_out_date=date.today() + timedelta(days=2)
            ),
            booking_status=BookingStatus.BOOKED,
        )

        assert reservation1 == reservation1

        reservation2 = Reservation(
            customer_id=CustomerID(value="CUST-001"),
            stay_period=StayPeriod(
                check_in_date=date.today() + timedelta(days=1), check_out_date=date.today() + timedelta(days=2)
            ),
            booking_status=BookingStatus.BOOKED,
        )

        assert reservation1 != reservation2  # Different IDs

    def test_reservation_hash(self, basic_reservation):
        """Test: Hash function works"""
        hash_value = hash(basic_reservation)
        assert isinstance(hash_value, int)

    def test_create_detail_with_empty_room_type(self):
        """Test: Empty room type"""
        # Room type validation tergantung implementasi
        # Jika tidak ada validasi, test ini bisa pass
        detail = ReservationDetail(
            room_id=RoomID(value="ROOM-001"),
            room_type="",  # Empty allowed or not?
            number_of_guests=1,
            price_per_night=Decimal("300000"),
        )
        # Just check it can be created
        assert detail.room_type == ""

    def test_create_detail_with_zero_price(self):
        """Test: Zero price (promotional rooms)"""
        detail = ReservationDetail(
            room_id=RoomID(value="ROOM-PROMO"), room_type="Promo", number_of_guests=1, price_per_night=Decimal("0")
        )
        assert detail.price_per_night == Decimal("0")

    def test_reservation_with_many_rooms(self):
        """Test: Reservation with 15 rooms"""
        reservation = Reservation(
            customer_id=CustomerID(value="CUST-BULK"),
            stay_period=StayPeriod(
                check_in_date=date.today() + timedelta(days=7), check_out_date=date.today() + timedelta(days=10)
            ),
            booking_status=BookingStatus.BOOKED,
        )

        for i in range(15):
            detail = ReservationDetail(
                room_id=RoomID(value=f"ROOM-{i}"),
                room_type="Standard",
                number_of_guests=1,
                price_per_night=Decimal("300000"),
            )
            reservation.add_reservation_detail(detail)

        assert len(reservation.reservation_details) == 15

    def test_state_transition_invalid_order(self):
        """Test: Skip PAID and go directly to CONFIRMED"""
        reservation = Reservation(
            customer_id=CustomerID(value="CUST-001"),
            stay_period=StayPeriod(
                check_in_date=date.today() + timedelta(days=1), check_out_date=date.today() + timedelta(days=2)
            ),
            booking_status=BookingStatus.BOOKED,
        )

        with pytest.raises(ValueError, match="must be paid before confirmation"):
            reservation.confirm_reservation()

    def test_create_detail_with_zero_price(self):
        """Test: Zero price (should be valid for promotional rooms)"""
        detail = ReservationDetail(
            room_id=RoomID(value="ROOM-001"), room_type="Promo", number_of_guests=1, price_per_night=Decimal("0")
        )
        assert detail.price_per_night == Decimal("0")
