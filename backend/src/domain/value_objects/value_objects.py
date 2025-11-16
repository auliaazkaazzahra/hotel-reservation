from datetime import date
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass
from typing import Optional


class BookingStatus(str, Enum):
    """Value Object: Status pemesanan"""
    BOOKED = "BOOKED"
    PAID = "PAID"
    CANCELLED = "CANCELLED"
    CONFIRMED = "CONFIRMED"


@dataclass(frozen=True)
class StayPeriod:
    """
    Value Object: Periode menginap
    """
    check_in_date: date
    check_out_date: date
    
    def __post_init__(self):
        if self.check_out_date <= self.check_in_date:
            raise ValueError("Check-out date must be after check-in date")
    
    def get_number_of_nights(self) -> int:
        """Hitung jumlah malam menginap"""
        return (self.check_out_date - self.check_in_date).days
    
    def __str__(self):
        return f"{self.check_in_date} to {self.check_out_date} ({self.get_number_of_nights()} nights)"


@dataclass(frozen=True)
class TotalAmount:
    """
    Value Object: Total harga pemesanan
    """
    amount: Decimal
    currency: str = "IDR"
    
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Total amount cannot be negative")
    
    def __str__(self):
        return f"{self.currency} {self.amount:,.2f}"


@dataclass(frozen=True)
class CustomerID:
    """Value Object: ID referensi ke Customer Context"""
    value: str
    
    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("CustomerID cannot be empty")


@dataclass(frozen=True)
class RoomID:
    """Value Object: ID referensi ke Room dalam Inventory Context"""
    value: str
    
    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("RoomID cannot be empty")


@dataclass(frozen=True)
class PaymentID:
    """Value Object: ID referensi ke Payment Context"""
    value: Optional[str] = None