from datetime import date
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from ..application.reservation_service import ReservationService
from ..infrastructure.auth import User
from ..infrastructure.reservation_repository import ReservationRepository
from .dependencies import get_current_active_user

# Inisialisasi dependency
repository = ReservationRepository()
service = ReservationService(repository)

# Router
router = APIRouter(prefix="/api/reservations", tags=["Reservations"])


# DTOs (Data Transfer Objects)


class RoomDetailRequest(BaseModel):
    """DTO untuk detail kamar dalam request"""

    room_id: str = Field(..., description="ID kamar dari Inventory Context")
    room_type: str = Field(default="Standard", description="Tipe kamar")
    number_of_guests: int = Field(default=1, ge=1, description="Jumlah tamu")
    price_per_night: Decimal = Field(..., ge=0, description="Harga per malam")

    class Config:
        json_schema_extra = {
            "example": {"room_id": "ROOM-001", "room_type": "Deluxe", "number_of_guests": 2, "price_per_night": 500000}
        }


class CreateReservationRequest(BaseModel):
    """DTO untuk membuat reservasi baru"""

    customer_id: str = Field(..., description="ID pelanggan")
    check_in_date: date = Field(..., description="Tanggal check-in")
    check_out_date: date = Field(..., description="Tanggal check-out")
    room_details: List[RoomDetailRequest] = Field(..., min_length=1)

    class Config:
        json_schema_extra = {
            "example": {
                "customer_id": "CUST-001",
                "check_in_date": "2025-12-01",
                "check_out_date": "2025-12-03",
                "room_details": [
                    {"room_id": "ROOM-001", "room_type": "Deluxe", "number_of_guests": 2, "price_per_night": 500000}
                ],
            }
        }


class AddRoomRequest(BaseModel):
    """DTO untuk menambah kamar ke reservasi"""

    room_id: str
    room_type: str = "Standard"
    number_of_guests: int = Field(default=1, ge=1)
    price_per_night: Decimal = Field(..., ge=0)


class ConfirmPaymentRequest(BaseModel):
    """DTO untuk konfirmasi pembayaran"""

    payment_id: str = Field(..., description="ID transaksi dari Payment Context")


class ReservationDetailResponse(BaseModel):
    """DTO untuk response detail kamar"""

    detail_id: str
    room_id: str
    room_type: str
    number_of_guests: int
    price_per_night: Decimal


class ReservationResponse(BaseModel):
    """DTO untuk response reservasi"""

    reservation_id: str
    customer_id: str
    check_in_date: date
    check_out_date: date
    number_of_nights: int
    booking_status: str
    reservation_details: List[ReservationDetailResponse]
    total_amount: Decimal
    currency: str
    payment_id: Optional[str] = None
    created_at: str
    updated_at: str


# ============= API Endpoints =============


@router.post(
    "/",
    response_model=ReservationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create New Reservation",
    description="Membuat reservasi baru dengan detail kamar",
)
async def create_reservation(request: CreateReservationRequest, current_user: User = Depends(get_current_active_user)):
    """
    Endpoint untuk membuat reservasi baru
    Requires: Valid JWT token
    """
    try:
        room_details_dict = [
            {
                "room_id": rd.room_id,
                "room_type": rd.room_type,
                "number_of_guests": rd.number_of_guests,
                "price_per_night": rd.price_per_night,
            }
            for rd in request.room_details
        ]

        reservation = service.create_reservation(
            customer_id=request.customer_id,
            check_in_date=request.check_in_date,
            check_out_date=request.check_out_date,
            room_details=room_details_dict,
        )

        return _map_to_response(reservation)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {str(e)}"
        )


@router.get(
    "/{reservation_id}",
    response_model=ReservationResponse,
    summary="Get Reservation by ID",
    description="Mengambil detail reservasi berdasarkan ID",
)
async def get_reservation(reservation_id: str, current_user: User = Depends(get_current_active_user)):
    """
    Endpoint untuk mengambil detail reservasi
    """
    reservation = service.get_reservation(reservation_id)

    if not reservation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Reservation {reservation_id} not found")

    return _map_to_response(reservation)


@router.get(
    "/",
    response_model=List[ReservationResponse],
    summary="Get All Reservations",
    description="Mengambil semua reservasi atau filter berdasarkan customer",
)
async def get_reservations(customer_id: Optional[str] = None, current_user: User = Depends(get_current_active_user)):
    """
    Endpoint untuk mengambil daftar reservasi
    Query param customer_id untuk filter berdasarkan customer
    """
    if customer_id:
        reservations = service.get_customer_reservations(customer_id)
    else:
        reservations = service.get_all_reservations()

    return [_map_to_response(r) for r in reservations]


@router.post(
    "/{reservation_id}/rooms",
    response_model=ReservationResponse,
    summary="Add Room to Reservation",
    description="Menambahkan kamar ke reservasi existing",
)
async def add_room_to_reservation(
    reservation_id: str, request: AddRoomRequest, current_user: User = Depends(get_current_active_user)
):
    """
    Endpoint untuk menambah kamar ke reservasi
    """
    try:
        reservation = service.add_room_to_reservation(
            reservation_id=reservation_id,
            room_id=request.room_id,
            room_type=request.room_type,
            number_of_guests=request.number_of_guests,
            price_per_night=request.price_per_night,
        )

        return _map_to_response(reservation)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/{reservation_id}/confirm-payment",
    response_model=ReservationResponse,
    summary="Confirm Payment",
    description="Konfirmasi pembayaran telah diterima",
)
async def confirm_payment(
    reservation_id: str, request: ConfirmPaymentRequest, current_user: User = Depends(get_current_active_user)
):
    """
    Endpoint untuk konfirmasi pembayaran
    """
    try:
        reservation = service.confirm_payment(reservation_id=reservation_id, payment_id=request.payment_id)

        return _map_to_response(reservation)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/{reservation_id}/confirm",
    response_model=ReservationResponse,
    summary="Confirm Reservation",
    description="Konfirmasi reservasi oleh pihak hotel",
)
async def confirm_reservation(reservation_id: str, current_user: User = Depends(get_current_active_user)):
    """
    Endpoint untuk konfirmasi reservasi oleh hotel
    """
    try:
        reservation = service.confirm_reservation(reservation_id)
        return _map_to_response(reservation)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/{reservation_id}/cancel",
    response_model=ReservationResponse,
    summary="Cancel Reservation",
    description="Membatalkan reservasi",
)
async def cancel_reservation(reservation_id: str, current_user: User = Depends(get_current_active_user)):
    """
    Endpoint untuk membatalkan reservasi
    """
    try:
        reservation = service.cancel_reservation(reservation_id)
        return _map_to_response(reservation)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/{reservation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Reservation",
    description="Menghapus reservasi (hard delete)",
)
async def delete_reservation(reservation_id: str, current_user: User = Depends(get_current_active_user)):
    """
    Endpoint untuk menghapus reservasi
    """
    success = service.delete_reservation(reservation_id)

    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Reservation {reservation_id} not found")

    return None


# ============= Helper Functions =============


def _map_to_response(reservation) -> ReservationResponse:
    """Helper untuk mapping domain model ke response DTO"""
    return ReservationResponse(
        reservation_id=reservation.reservation_id,
        customer_id=reservation.customer_id.value,
        check_in_date=reservation.stay_period.check_in_date,
        check_out_date=reservation.stay_period.check_out_date,
        number_of_nights=reservation.stay_period.get_number_of_nights(),
        booking_status=reservation.booking_status.value,
        reservation_details=[
            ReservationDetailResponse(
                detail_id=detail.detail_id,
                room_id=detail.room_id.value,
                room_type=detail.room_type,
                number_of_guests=detail.number_of_guests,
                price_per_night=detail.price_per_night,
            )
            for detail in reservation.reservation_details
        ],
        total_amount=reservation.total_amount.amount,
        currency=reservation.total_amount.currency,
        payment_id=reservation.payment_id.value if reservation.payment_id and reservation.payment_id.value else None,
        created_at=reservation.created_at.isoformat(),
        updated_at=reservation.updated_at.isoformat(),
    )
