import uuid
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional

from ..value_objects.value_objects import RoomID


@dataclass
class ReservationDetail:
    """
    Entity: Detail kamar yang dipesan
    Merepresentasikan satu kamar dalam pemesanan
    """

    detail_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    room_id: RoomID = None
    room_type: str = ""
    number_of_guests: int = 1
    price_per_night: Decimal = Decimal("0.00")

    def __post_init__(self):
        """Validasi data detail reservasi"""
        if self.room_id is None:
            raise ValueError("RoomID is required")

        if self.number_of_guests < 1:
            raise ValueError("Number of guests must be at least 1")

        if self.price_per_night < 0:
            raise ValueError("Price per night cannot be negative")

    def calculate_subtotal(self, number_of_nights: int) -> Decimal:
        """Hitung subtotal untuk detail ini"""
        if number_of_nights < 1:
            raise ValueError("Number of nights must be at least 1")

        return self.price_per_night * number_of_nights

    def __eq__(self, other):
        """Equality berdasarkan detail_id"""
        if not isinstance(other, ReservationDetail):
            return False
        return self.detail_id == other.detail_id

    def __hash__(self):
        return hash(self.detail_id)
