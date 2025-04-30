from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from app.utils.database_utils import (
    create_resident, get_resident_by_tg_id, create_car, get_car_by_plate_and_owner,
    get_free_parking_spots, create_booking, cancel_booking, get_resident_bookings
)
from app.db.database import SessionLocal
from app.db.models import ParkingSpot

router = APIRouter(prefix="/booking", tags=["Booking"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register", tags=["Booking"])
async def register_resident(tg_id: int, db: Session = Depends(get_db)):
    """
    Эндпоинт для регистрации жителя.
    """
    existing_resident = get_resident_by_tg_id(db, tg_id)
    if existing_resident:
        raise HTTPException(status_code=400, detail="Resident with this tg_id already exists")

    new_resident = create_resident(db, tg_id)
    return {"message": "Resident registered successfully", "id": new_resident.id}


@router.post("/register-car", tags=["Booking"])
async def register_car(tg_id: int, car_plate: str, db: Session = Depends(get_db)):
    """
    Эндпоинт для регистрации номера машины.
    """
    resident = get_resident_by_tg_id(db, tg_id)
    if not resident:
        raise HTTPException(status_code=404, detail="Resident not found")

    existing_car = get_car_by_plate_and_owner(db, car_plate, resident.id)
    if existing_car:
        raise HTTPException(status_code=400, detail="Car with this plate already exists")

    new_car = create_car(db, resident.id, car_plate)
    return {"message": "Car registered successfully", "id": new_car.id}


@router.get("/get-free-spots", tags=["Booking"])
async def get_free_spots(db: Session = Depends(get_db)):
    """
    Эндпоинт для получения свободных парковочных мест.
    """
    free_spots = get_free_parking_spots(db)
    spots_list = [{"id": spot.id, "parking_spot_number": spot.parking_spot_number, "description": spot.description} for spot in free_spots]
    return spots_list


@router.post("/reserve-parking", tags=["Booking"])
async def reserve_parking(tg_id: int, place_id: int, car_plate: str, start_time: float, end_time: float,
                          db: Session = Depends(get_db)):
    """
    Эндпоинт для бронирования парковочного места.
    """
    resident = get_resident_by_tg_id(db, tg_id)
    if not resident:
        raise HTTPException(status_code=404, detail="Resident not found")

    car = get_car_by_plate_and_owner(db, car_plate, resident.id)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    spot = db.query(ParkingSpot).filter_by(id=place_id).first()
    if not spot or spot.is_reserved:
        raise HTTPException(status_code=400, detail="Parking spot is not available")

    booking = create_booking(db, resident.id, spot.id, car.car_plate, datetime.fromtimestamp(start_time),
                             datetime.fromtimestamp(end_time))
    return {"message": "Spot booked successfully", "booking_id": booking.id}


@router.delete("/cancel-reservation/{reservation_id}", tags=["Booking"])
async def cancel_reservation(reservation_id: int, db: Session = Depends(get_db)):
    """
    Эндпоинт для снятия брони.
    """
    booking = cancel_booking(db, reservation_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return {"message": "Reservation canceled successfully"}


@router.get("/view-reservations", tags=["Booking"])
async def view_reservations(tg_id: int, db: Session = Depends(get_db)):
    """
    Эндпоинт для просмотра бронирований.
    """
    resident = get_resident_by_tg_id(db, tg_id)
    if not resident:
        raise HTTPException(status_code=404, detail="Resident not found")

    bookings = get_resident_bookings(db, resident.id)
    bookings_list = [
        {
            "id": booking.id,
            "spot_id": booking.spot_id,
            "car_plate": booking.car_plate,
            "start_time": booking.start_time.timestamp(),
            "end_time": booking.end_time.timestamp()
        } for booking in bookings
    ]
    return bookings_list