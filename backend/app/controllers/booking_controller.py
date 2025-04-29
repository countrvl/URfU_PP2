from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from .database import get_db, Resident, Car, ParkingSpot, Booking, Log

router = APIRouter(prefix="/booking", tags=["Booking"])


def get_db_session(db: Session = Depends(get_db)):
    try:
        yield db
    finally:
        db.close()


@router.post("/register", tags=["Registration"])
async def register_resident(tg_id: int, db: Session = Depends(get_db_session)):
    """
    Эндпоинт для регистрации жителя.
    """
    existing_resident = db.query(Resident).filter_by(tg_id=tg_id).first()
    if existing_resident:
        raise HTTPException(status_code=400, detail="Resident with this tg_id already exists")

    new_resident = Resident(tg_id=tg_id)
    db.add(new_resident)
    db.commit()
    db.refresh(new_resident)
    return {"message": "Resident registered successfully", "id": new_resident.id}


@router.post("/register-car", tags=["Registration"])
async def register_car(tg_id: int, car_plate: str, db: Session = Depends(get_db_session)):
    """
    Эндпоинт для регистрации номера машины.
    """
    resident = db.query(Resident).filter_by(tg_id=tg_id).first()
    if not resident:
        raise HTTPException(status_code=404, detail="Resident not found")

    existing_car = db.query(Car).filter_by(car_plate=car_plate).first()
    if existing_car:
        raise HTTPException(status_code=400, detail="Car with this plate already exists")

    new_car = Car(car_plate=car_plate, owner_id=resident.id)
    db.add(new_car)
    db.commit()
    db.refresh(new_car)
    return {"message": "Car registered successfully", "id": new_car.id}


@router.get("/get-free-spots", tags=["Parking"])
async def get_free_spots(db: Session = Depends(get_db_session)):
    """
    Эндпоинт для получения свободных парковочных мест.
    """
    free_spots = db.query(ParkingSpot).filter_by(is_reserved=False).all()
    spots_list = [{"id": spot.id, "description": spot.description} for spot in free_spots]
    return spots_list


@router.post("/reserve-parking", tags=["Booking"])
async def reserve_parking(tg_id: int, place_id: int, car_plate: str, start_time: float, end_time: float,
                          db: Session = Depends(get_db_session)):
    """
    Эндпоинт для бронирования парковочного места.
    """
    resident = db.query(Resident).filter_by(tg_id=tg_id).first()
    if not resident:
        raise HTTPException(status_code=404, detail="Resident not found")

    car = db.query(Car).filter_by(car_plate=car_plate, owner_id=resident.id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    spot = db.query(ParkingSpot).filter_by(id=place_id).first()
    if not spot or spot.is_reserved:
        raise HTTPException(status_code=400, detail="Parking spot is not available")

    booking = Booking(
        resident_id=resident.id,
        spot_id=spot.id,
        car_plate=car.car_plate,
        start_time=datetime.fromtimestamp(start_time),
        end_time=datetime.fromtimestamp(end_time)
    )

    spot.is_reserved = True
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return {"message": "Spot booked successfully", "booking_id": booking.id}


@router.delete("/cancel-reservation/{reservation_id}", tags=["Booking"])
async def cancel_reservation(reservation_id: int, db: Session = Depends(get_db_session)):
    """
    Эндпоинт для снятия брони.
    """
    booking = db.query(Booking).filter_by(id=reservation_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    spot = db.query(ParkingSpot).filter_by(id=booking.spot_id).first()
    if not spot:
        raise HTTPException(status_code=404, detail="Parking spot not found")

    spot.is_reserved = False
    db.delete(booking)
    db.commit()
    return {"message": "Reservation canceled successfully"}


@router.get("/view-reservations", tags=["Booking"])
async def view_reservations(tg_id: int, db: Session = Depends(get_db_session)):
    """
    Эндпоинт для просмотра бронирований.
    """
    resident = db.query(Resident).filter_by(tg_id=tg_id).first()
    if not resident:
        raise HTTPException(status_code=404, detail="Resident not found")

    bookings = db.query(Booking).filter_by(resident_id=resident.id).all()
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