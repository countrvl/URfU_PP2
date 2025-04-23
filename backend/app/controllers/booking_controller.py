from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/booking", tags=["Booking"])

@router.post("/process-license")
async def process_license(license_number: str):
    """
    Эндпоинт для обработки номера машины.
    """
    # Заглушка
    return {"message": f"Processing license number: {license_number}"}

@router.post("/reserve-parking")
async def reserve_parking(user_id: int, parking_spot_id: int):
    """
    Эндпоинт для бронирования парковочного места.
    """
    # Заглушка
    return {"message": f"Parking spot {parking_spot_id} reserved for user {user_id}"}

@router.delete("/cancel-reservation/{reservation_id}")
async def cancel_reservation(reservation_id: int):
    """
    Эндпоинт для снятия брони.
    """
    # Заглушка
    return {"message": f"Reservation {reservation_id} canceled"}

@router.get("/view-reservations")
async def view_reservations():
    """
    Эндпоинт для просмотра бронирований.
    """
    # Заглушка
    return {"message": "No reservations found"}