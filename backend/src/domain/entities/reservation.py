from datetime import datetime
from decimal import Decimal
from dataclasses import dataclass, field
from typing import List, Optional
import uuid

from ..value_objects.value_objects import (
    BookingStatus, 
    StayPeriod, 
    TotalAmount, 
    CustomerID, 
    PaymentID
)
from .reservation_detail import ReservationDetail


@dataclass
class Reservation:
    """
    Aggregate Root: Reservation
    Mengelola seluruh proses pemesanan kamar hotel
    """
    reservation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: CustomerID = None
    stay_period: StayPeriod = None
    booking_status: BookingStatus = BookingStatus.BOOKED
    reservation_details: List[ReservationDetail] = field(default_factory=list)
    total_amount: Optional[TotalAmount] = None
    payment_id: Optional[PaymentID] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validasi data reservasi"""
        if self.customer_id is None:
            raise ValueError("CustomerID is required")
        
        if self.stay_period is None:
            raise ValueError("StayPeriod is required")
        
        # Hitung total amount jika belum ada
        if self.total_amount is None and self.reservation_details:
            self.calculate_total_amount()
    
    def add_reservation_detail(self, detail: ReservationDetail) -> None:
        """Tambahkan detail kamar ke reservasi"""
        if not isinstance(detail, ReservationDetail):
            raise TypeError("Detail must be ReservationDetail instance")
        
        # Cek apakah room sudah ada dalam reservasi
        if any(d.room_id == detail.room_id for d in self.reservation_details):
            raise ValueError(f"Room {detail.room_id.value} already added to this reservation")
        
        self.reservation_details.append(detail)
        self.calculate_total_amount()
        self.updated_at = datetime.now()
    
    def remove_reservation_detail(self, detail_id: str) -> None:
        """Hapus detail kamar dari reservasi"""
        initial_length = len(self.reservation_details)
        self.reservation_details = [d for d in self.reservation_details if d.detail_id != detail_id]
        
        if len(self.reservation_details) == initial_length:
            raise ValueError(f"Detail with ID {detail_id} not found")
        
        self.calculate_total_amount()
        self.updated_at = datetime.now()
    
    def calculate_total_amount(self) -> None:
        """Hitung total harga berdasarkan detail kamar dan periode inap"""
        if not self.reservation_details:
            self.total_amount = TotalAmount(amount=Decimal('0.00'))
            return
        
        number_of_nights = self.stay_period.get_number_of_nights()
        total = sum(
            detail.calculate_subtotal(number_of_nights) 
            for detail in self.reservation_details
        )
        
        self.total_amount = TotalAmount(amount=total)
    
    def confirm_payment(self, payment_id: str) -> None:
        """Konfirmasi pembayaran telah diterima"""
        if self.booking_status == BookingStatus.CANCELLED:
            raise ValueError("Cannot confirm payment for cancelled reservation")
        
        self.payment_id = PaymentID(value=payment_id)
        self.booking_status = BookingStatus.PAID
        self.updated_at = datetime.now()
    
    def confirm_reservation(self) -> None:
        """Konfirmasi reservasi oleh hotel"""
        if self.booking_status != BookingStatus.PAID:
            raise ValueError("Reservation must be paid before confirmation")
        
        self.booking_status = BookingStatus.CONFIRMED
        self.updated_at = datetime.now()
    
    def cancel_reservation(self) -> None:
        """Batalkan reservasi"""
        if self.booking_status == BookingStatus.CONFIRMED:
            raise ValueError("Cannot cancel confirmed reservation")
        
        self.booking_status = BookingStatus.CANCELLED
        self.updated_at = datetime.now()
    
    def is_modifiable(self) -> bool:
        """Cek apakah reservasi masih bisa dimodifikasi"""
        return self.booking_status in [BookingStatus.BOOKED, BookingStatus.PAID]
    
    def __eq__(self, other):
        """Equality berdasarkan reservation_id"""
        if not isinstance(other, Reservation):
            return False
        return self.reservation_id == other.reservation_id
    
    def __hash__(self):
        return hash(self.reservation_id)