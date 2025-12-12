from dataclasses import asdict
from datetime import date
from decimal import Decimal
from typing import List, Optional

from ..domain.entities.reservation import Reservation
from ..domain.entities.reservation_detail import ReservationDetail
from ..domain.value_objects.value_objects import BookingStatus, CustomerID, RoomID, StayPeriod
from ..infrastructure.reservation_repository import ReservationRepository


class ReservationService:
    """
    Application Service untuk mengelola use case Reservation
    Bertindak sebagai orchestrator untuk business logic
    """

    def __init__(self, repository: ReservationRepository):
        self.repository = repository

    def create_reservation(
        self, customer_id: str, check_in_date: date, check_out_date: date, room_details: List[dict]
    ) -> Reservation:
        """
        Use Case: Membuat reservasi baru

        Args:
            customer_id: ID pelanggan
            check_in_date: Tanggal check-in
            check_out_date: Tanggal check-out
            room_details: List detail kamar [
                {
                    "room_id": str,
                    "room_type": str,
                    "number_of_guests": int,
                    "price_per_night": Decimal
                }
            ]

        Returns:
            Reservation yang telah dibuat
        """
        # Buat value objects
        customer = CustomerID(value=customer_id)
        stay_period = StayPeriod(check_in_date=check_in_date, check_out_date=check_out_date)

        # Buat reservation aggregate
        reservation = Reservation(customer_id=customer, stay_period=stay_period, booking_status=BookingStatus.BOOKED)

        # Tambahkan detail kamar
        for room_detail in room_details:
            detail = ReservationDetail(
                room_id=RoomID(value=room_detail["room_id"]),
                room_type=room_detail.get("room_type", "Standard"),
                number_of_guests=room_detail.get("number_of_guests", 1),
                price_per_night=Decimal(str(room_detail.get("price_per_night", 0))),
            )
            reservation.add_reservation_detail(detail)

        # Simpan ke repository
        return self.repository.save(reservation)

    def get_reservation(self, reservation_id: str) -> Optional[Reservation]:
        """Use Case: Mengambil detail reservasi"""
        return self.repository.find_by_id(reservation_id)

    def get_customer_reservations(self, customer_id: str) -> List[Reservation]:
        """Use Case: Mengambil semua reservasi customer"""
        return self.repository.find_by_customer_id(customer_id)

    def get_all_reservations(self) -> List[Reservation]:
        """Use Case: Mengambil semua reservasi"""
        return self.repository.find_all()

    def add_room_to_reservation(
        self, reservation_id: str, room_id: str, room_type: str, number_of_guests: int, price_per_night: Decimal
    ) -> Reservation:
        """Use Case: Menambah kamar ke reservasi existing"""
        reservation = self.repository.find_by_id(reservation_id)
        if not reservation:
            raise ValueError(f"Reservation {reservation_id} not found")

        if not reservation.is_modifiable():
            raise ValueError("Cannot modify this reservation")

        detail = ReservationDetail(
            room_id=RoomID(value=room_id),
            room_type=room_type,
            number_of_guests=number_of_guests,
            price_per_night=price_per_night,
        )

        reservation.add_reservation_detail(detail)
        return self.repository.save(reservation)

    def confirm_payment(self, reservation_id: str, payment_id: str) -> Reservation:
        """Use Case: Konfirmasi pembayaran"""
        reservation = self.repository.find_by_id(reservation_id)
        if not reservation:
            raise ValueError(f"Reservation {reservation_id} not found")

        reservation.confirm_payment(payment_id)
        return self.repository.save(reservation)

    def confirm_reservation(self, reservation_id: str) -> Reservation:
        """Use Case: Konfirmasi reservasi oleh hotel"""
        reservation = self.repository.find_by_id(reservation_id)
        if not reservation:
            raise ValueError(f"Reservation {reservation_id} not found")

        reservation.confirm_reservation()
        return self.repository.save(reservation)

    def cancel_reservation(self, reservation_id: str) -> Reservation:
        """Use Case: Batalkan reservasi"""
        reservation = self.repository.find_by_id(reservation_id)
        if not reservation:
            raise ValueError(f"Reservation {reservation_id} not found")

        reservation.cancel_reservation()
        return self.repository.save(reservation)

    def delete_reservation(self, reservation_id: str) -> bool:
        """Use Case: Hapus reservasi (hard delete)"""
        return self.repository.delete(reservation_id)
