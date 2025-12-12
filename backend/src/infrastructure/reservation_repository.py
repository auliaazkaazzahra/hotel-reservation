from typing import Dict, List, Optional

from ..domain.entities.reservation import Reservation


class ReservationRepository:
    """
    Repository untuk mengelola persistence Reservation
    Menggunakan in-memory storage untuk development
    """

    def __init__(self):
        self._storage: Dict[str, Reservation] = {}

    def save(self, reservation: Reservation) -> Reservation:
        """
        Simpan atau update reservasi

        Args:
            reservation: Instance Reservation yang akan disimpan

        Returns:
            Reservation yang telah disimpan
        """
        self._storage[reservation.reservation_id] = reservation
        return reservation

    def find_by_id(self, reservation_id: str) -> Optional[Reservation]:
        """
        Cari reservasi berdasarkan ID

        Args:
            reservation_id: ID unik reservasi

        Returns:
            Reservation jika ditemukan, None jika tidak
        """
        return self._storage.get(reservation_id)

    def find_by_customer_id(self, customer_id: str) -> List[Reservation]:
        """
        Cari semua reservasi milik customer tertentu

        Args:
            customer_id: ID customer

        Returns:
            List of Reservation
        """
        return [reservation for reservation in self._storage.values() if reservation.customer_id.value == customer_id]

    def find_all(self) -> List[Reservation]:
        """
        Ambil semua reservasi

        Returns:
            List of all Reservation
        """
        return list(self._storage.values())

    def delete(self, reservation_id: str) -> bool:
        """
        Hapus reservasi berdasarkan ID

        Args:
            reservation_id: ID reservasi yang akan dihapus

        Returns:
            True jika berhasil, False jika tidak ditemukan
        """
        if reservation_id in self._storage:
            del self._storage[reservation_id]
            return True
        return False

    def clear(self) -> None:
        """
        Hapus semua data (untuk testing)
        """
        self._storage.clear()
