"""
Unit tests untuk Value Objects
Coverage: Validasi, edge cases, dan error handling
"""
from datetime import date, timedelta
from decimal import Decimal

import pytest

from src.domain.value_objects.value_objects import BookingStatus, CustomerID, PaymentID, RoomID, StayPeriod, TotalAmount


class TestStayPeriod:
    """Test StayPeriod Value Object"""

    def test_valid_stay_period(self):
        """Test: Valid stay period dapat dibuat"""
        check_in = date.today()
        check_out = date.today() + timedelta(days=3)

        period = StayPeriod(check_in_date=check_in, check_out_date=check_out)

        assert period.check_in_date == check_in
        assert period.check_out_date == check_out
        assert period.get_number_of_nights() == 3

    def test_stay_period_one_night(self):
        """Test: Stay period 1 malam"""
        check_in = date.today()
        check_out = check_in + timedelta(days=1)

        period = StayPeriod(check_in_date=check_in, check_out_date=check_out)
        assert period.get_number_of_nights() == 1

    def test_stay_period_multiple_nights(self):
        """Test: Stay period multiple nights"""
        check_in = date(2025, 12, 1)
        check_out = date(2025, 12, 10)

        period = StayPeriod(check_in_date=check_in, check_out_date=check_out)
        assert period.get_number_of_nights() == 9

    def test_invalid_stay_period_same_date(self):
        """Test: Check-out sama dengan check-in harus error"""
        same_date = date.today()

        with pytest.raises(ValueError, match="Check-out date must be after check-in date"):
            StayPeriod(check_in_date=same_date, check_out_date=same_date)

    def test_invalid_stay_period_past_checkout(self):
        """Test: Check-out sebelum check-in harus error"""
        check_in = date.today()
        check_out = date.today() - timedelta(days=1)

        with pytest.raises(ValueError, match="Check-out date must be after check-in date"):
            StayPeriod(check_in_date=check_in, check_out_date=check_out)

    def test_invalid_stay_period_checkout_before_checkin(self):
        """Test: Check-out jauh sebelum check-in"""
        check_in = date(2025, 12, 10)
        check_out = date(2025, 12, 1)

        with pytest.raises(ValueError):
            StayPeriod(check_in_date=check_in, check_out_date=check_out)

    def test_stay_period_immutability(self):
        """Test: StayPeriod immutable (frozen dataclass)"""
        period = StayPeriod(check_in_date=date.today(), check_out_date=date.today() + timedelta(days=2))

        with pytest.raises(Exception):  # FrozenInstanceError or AttributeError
            period.check_in_date = date.today() + timedelta(days=1)

    def test_stay_period_string_representation(self):
        """Test: String representation"""
        check_in = date(2025, 12, 1)
        check_out = date(2025, 12, 5)
        period = StayPeriod(check_in_date=check_in, check_out_date=check_out)

        str_repr = str(period)
        assert "2025-12-01" in str_repr
        assert "2025-12-05" in str_repr
        assert "4 nights" in str_repr

    def test_stay_period_equality(self):
        """Test: Equality comparison"""
        check_in = date(2025, 12, 1)
        check_out = date(2025, 12, 5)

        period1 = StayPeriod(check_in_date=check_in, check_out_date=check_out)
        period2 = StayPeriod(check_in_date=check_in, check_out_date=check_out)

        assert period1 == period2

    def test_stay_period_inequality(self):
        """Test: Inequality comparison"""
        period1 = StayPeriod(check_in_date=date(2025, 12, 1), check_out_date=date(2025, 12, 5))
        period2 = StayPeriod(check_in_date=date(2025, 12, 1), check_out_date=date(2025, 12, 10))

        assert period1 != period2


class TestBookingStatus:
    """Test BookingStatus Enum"""

    def test_all_status_exists(self):
        """Test: Semua status terdefinisi"""
        assert BookingStatus.BOOKED
        assert BookingStatus.PAID
        assert BookingStatus.CONFIRMED
        assert BookingStatus.CANCELLED

    def test_status_values(self):
        """Test: Nilai status sesuai"""
        assert BookingStatus.BOOKED.value == "BOOKED"
        assert BookingStatus.PAID.value == "PAID"
        assert BookingStatus.CONFIRMED.value == "CONFIRMED"
        assert BookingStatus.CANCELLED.value == "CANCELLED"

    def test_status_comparison(self):
        """Test: Status comparison"""
        status1 = BookingStatus.BOOKED
        status2 = BookingStatus.BOOKED
        status3 = BookingStatus.PAID

        assert status1 == status2
        assert status1 != status3

    def test_status_string_representation(self):
        """Test: String representation"""
        assert BookingStatus.BOOKED.value == "BOOKED"
        assert BookingStatus.PAID.value == "PAID"
        assert "BOOKED" in str(BookingStatus.BOOKED)

    def test_status_is_string_enum(self):
        """Test: BookingStatus is string enum"""
        assert isinstance(BookingStatus.BOOKED, str)
        assert isinstance(BookingStatus.BOOKED.value, str)


class TestTotalAmount:
    """Test TotalAmount Value Object"""

    def test_valid_amount(self):
        """Test: Valid amount dapat dibuat"""
        amount = TotalAmount(amount=Decimal("1500000"))

        assert amount.amount == Decimal("1500000")
        assert amount.currency == "IDR"

    def test_amount_with_custom_currency(self):
        """Test: Custom currency"""
        amount = TotalAmount(amount=Decimal("100"), currency="USD")

        assert amount.amount == Decimal("100")
        assert amount.currency == "USD"

    def test_amount_with_different_currencies(self):
        """Test: Different currencies"""
        idr = TotalAmount(amount=Decimal("1000000"), currency="IDR")
        usd = TotalAmount(amount=Decimal("100"), currency="USD")
        eur = TotalAmount(amount=Decimal("90"), currency="EUR")

        assert idr.currency == "IDR"
        assert usd.currency == "USD"
        assert eur.currency == "EUR"

    def test_zero_amount(self):
        """Test: Zero amount valid"""
        amount = TotalAmount(amount=Decimal("0"))
        assert amount.amount == Decimal("0")

    def test_negative_amount(self):
        """Test: Negative amount tidak valid"""
        with pytest.raises(ValueError, match="Total amount cannot be negative"):
            TotalAmount(amount=Decimal("-100"))

    def test_large_negative_amount(self):
        """Test: Large negative amount"""
        with pytest.raises(ValueError):
            TotalAmount(amount=Decimal("-1000000"))

    def test_amount_precision(self):
        """Test: Decimal precision"""
        amount = TotalAmount(amount=Decimal("1500000.50"))
        assert amount.amount == Decimal("1500000.50")

    def test_amount_high_precision(self):
        """Test: High precision decimal"""
        amount = TotalAmount(amount=Decimal("1500000.999"))
        assert amount.amount == Decimal("1500000.999")

    def test_amount_immutability(self):
        """Test: TotalAmount immutable"""
        amount = TotalAmount(amount=Decimal("1000"))

        with pytest.raises(Exception):  # FrozenInstanceError
            amount.amount = Decimal("2000")

    def test_amount_string_representation(self):
        """Test: String representation"""
        amount = TotalAmount(amount=Decimal("1500000"), currency="IDR")
        str_repr = str(amount)

        assert "IDR" in str_repr
        assert "1500000" in str_repr or "1,500,000" in str_repr

    def test_amount_equality(self):
        """Test: Equality comparison"""
        amount1 = TotalAmount(amount=Decimal("1000"), currency="IDR")
        amount2 = TotalAmount(amount=Decimal("1000"), currency="IDR")

        assert amount1 == amount2

    def test_amount_inequality_different_value(self):
        """Test: Inequality with different amount"""
        amount1 = TotalAmount(amount=Decimal("1000"), currency="IDR")
        amount2 = TotalAmount(amount=Decimal("2000"), currency="IDR")

        assert amount1 != amount2

    def test_amount_inequality_different_currency(self):
        """Test: Inequality with different currency"""
        amount1 = TotalAmount(amount=Decimal("1000"), currency="IDR")
        amount2 = TotalAmount(amount=Decimal("1000"), currency="USD")

        assert amount1 != amount2


class TestCustomerID:
    """Test CustomerID Value Object"""

    def test_customer_id_valid(self):
        """Test: Valid CustomerID"""
        customer = CustomerID(value="CUST-001")
        assert customer.value == "CUST-001"

    def test_customer_id_different_formats(self):
        """Test: Different ID formats"""
        customer1 = CustomerID(value="CUST-001")
        customer2 = CustomerID(value="USER-123")
        customer3 = CustomerID(value="12345")

        assert customer1.value == "CUST-001"
        assert customer2.value == "USER-123"
        assert customer3.value == "12345"

    def test_customer_id_empty(self):
        """Test: Empty CustomerID tidak valid"""
        with pytest.raises(ValueError, match="CustomerID cannot be empty"):
            CustomerID(value="")

    def test_customer_id_whitespace(self):
        """Test: Whitespace only CustomerID tidak valid"""
        with pytest.raises(ValueError, match="CustomerID cannot be empty"):
            CustomerID(value="   ")

    def test_customer_id_immutability(self):
        """Test: CustomerID immutable"""
        customer = CustomerID(value="CUST-001")

        with pytest.raises(Exception):
            customer.value = "CUST-002"

    def test_customer_id_equality(self):
        """Test: Equality comparison"""
        customer1 = CustomerID(value="CUST-001")
        customer2 = CustomerID(value="CUST-001")

        assert customer1 == customer2

    def test_customer_id_inequality(self):
        """Test: Inequality comparison"""
        customer1 = CustomerID(value="CUST-001")
        customer2 = CustomerID(value="CUST-002")

        assert customer1 != customer2


class TestRoomID:
    """Test RoomID Value Object"""

    def test_room_id_valid(self):
        """Test: Valid RoomID"""
        room = RoomID(value="ROOM-101")
        assert room.value == "ROOM-101"

    def test_room_id_different_formats(self):
        """Test: Different room ID formats"""
        room1 = RoomID(value="ROOM-101")
        room2 = RoomID(value="R-202")
        room3 = RoomID(value="301")

        assert room1.value == "ROOM-101"
        assert room2.value == "R-202"
        assert room3.value == "301"

    def test_room_id_empty(self):
        """Test: Empty RoomID tidak valid"""
        with pytest.raises(ValueError, match="RoomID cannot be empty"):
            RoomID(value="")

    def test_room_id_whitespace(self):
        """Test: Whitespace only RoomID tidak valid"""
        with pytest.raises(ValueError):
            RoomID(value="   ")

    def test_room_id_immutability(self):
        """Test: RoomID immutable"""
        room = RoomID(value="ROOM-101")

        with pytest.raises(Exception):
            room.value = "ROOM-102"

    def test_room_id_equality(self):
        """Test: Equality comparison"""
        room1 = RoomID(value="ROOM-101")
        room2 = RoomID(value="ROOM-101")

        assert room1 == room2

    def test_room_id_inequality(self):
        """Test: Inequality comparison"""
        room1 = RoomID(value="ROOM-101")
        room2 = RoomID(value="ROOM-102")

        assert room1 != room2


class TestPaymentID:
    """Test PaymentID Value Object"""

    def test_payment_id_valid(self):
        """Test: Valid PaymentID"""
        payment = PaymentID(value="PAY-12345")
        assert payment.value == "PAY-12345"

    def test_payment_id_different_formats(self):
        """Test: Different payment ID formats"""
        payment1 = PaymentID(value="PAY-12345")
        payment2 = PaymentID(value="TRX-67890")
        payment3 = PaymentID(value="INV-001")

        assert payment1.value == "PAY-12345"
        assert payment2.value == "TRX-67890"
        assert payment3.value == "INV-001"

    def test_payment_id_none(self):
        """Test: PaymentID dapat None (belum bayar)"""
        payment = PaymentID(value=None)
        assert payment.value is None

    def test_payment_id_none_default(self):
        """Test: PaymentID default None"""
        payment = PaymentID()
        assert payment.value is None

    def test_payment_id_immutability(self):
        """Test: PaymentID immutable"""
        payment = PaymentID(value="PAY-001")

        with pytest.raises(Exception):
            payment.value = "PAY-002"

    def test_payment_id_equality(self):
        """Test: Equality comparison"""
        payment1 = PaymentID(value="PAY-001")
        payment2 = PaymentID(value="PAY-001")

        assert payment1 == payment2

    def test_payment_id_inequality(self):
        """Test: Inequality comparison"""
        payment1 = PaymentID(value="PAY-001")
        payment2 = PaymentID(value="PAY-002")

        assert payment1 != payment2

    def test_payment_id_none_equality(self):
        """Test: None PaymentID equality"""
        payment1 = PaymentID(value=None)
        payment2 = PaymentID(value=None)

        assert payment1 == payment2


class TestValueObjectsIntegration:
    """Test integrasi antar Value Objects"""

    def test_multiple_value_objects_together(self):
        """Test: Gunakan multiple value objects bersama"""
        stay_period = StayPeriod(check_in_date=date(2025, 12, 1), check_out_date=date(2025, 12, 5))
        customer_id = CustomerID(value="CUST-001")
        room_id = RoomID(value="ROOM-101")
        total_amount = TotalAmount(amount=Decimal("2000000"))
        payment_id = PaymentID(value="PAY-001")
        status = BookingStatus.CONFIRMED

        assert stay_period.get_number_of_nights() == 4
        assert customer_id.value == "CUST-001"
        assert room_id.value == "ROOM-101"
        assert total_amount.amount == Decimal("2000000")
        assert payment_id.value == "PAY-001"
        assert status == BookingStatus.CONFIRMED
