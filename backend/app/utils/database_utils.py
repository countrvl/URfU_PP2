from sqlalchemy.orm import Session
from app.db.models import Resident, Car, ParkingSpot, Booking, Log
from datetime import datetime

# Создание записи в таблице Residents
def create_resident(db: Session, tg_id: int):
    resident = Resident(tg_id=tg_id)
    db.add(resident)
    db.commit()
    db.refresh(resident)
    return resident


# Получение всех жителей
def get_all_residents(db: Session):
    return db.query(Resident).all()

# Обновление имени жителя
def update_resident(db: Session, resident_id: int, new_name: str):
    resident = db.query(Resident).filter(Resident.id == resident_id).first()
    if resident:
        resident.name = new_name
        db.commit()
        db.refresh(resident)
    return resident

# Удаление жителя
def delete_resident(db: Session, resident_id: int):
    resident = db.query(Resident).filter(Resident.id == resident_id).first()
    if resident:
        db.delete(resident)
        db.commit()
    return resident

# Создание парковочного места
def create_parking_spot(db: Session, parking_spot_number: str, description: str):
    spot = ParkingSpot(parking_spot_number=parking_spot_number, description=description, is_reserved=False)
    db.add(spot)
    db.commit()
    db.refresh(spot)
    return spot

# Получение всех парковочных мест
def get_all_parking_spots(db: Session):
    return db.query(ParkingSpot).all()

# Обновление описания парковочного места
def update_parking_spot(db: Session, spot_id: int, new_description: str):
    spot = db.query(ParkingSpot).filter(ParkingSpot.id == spot_id).first()
    if spot:
        spot.description = new_description
        db.commit()
        db.refresh(spot)
    return spot

# Удаление парковочного места
def delete_parking_spot(db: Session, spot_id: int):
    spot = db.query(ParkingSpot).filter(ParkingSpot.id == spot_id).first()
    if spot:
        db.delete(spot)
        db.commit()
    return spot

# Получение жителя по tg_id
def get_resident_by_tg_id(db: Session, tg_id: int):
    return db.query(Resident).filter(Resident.tg_id == tg_id).first()

# Создание записи в таблице Cars
def create_car(db: Session, resident_id: int, car_plate: str):
    car = Car(car_plate=car_plate, owner_id=resident_id)
    db.add(car)
    db.commit()
    db.refresh(car)
    return car

# Получение автомобиля по car_plate и owner_id
def get_car_by_plate_and_owner(db: Session, car_plate: str, owner_id: int):
    return db.query(Car).filter(Car.car_plate == car_plate, Car.owner_id == owner_id).first()

# Получение всех парковочных мест
def get_all_parking_spots(db: Session):
    return db.query(ParkingSpot).all()

# Получение свободных парковочных мест
def get_free_parking_spots(db: Session):
    return db.query(ParkingSpot).filter_by(is_reserved=False).all()

# Создание бронирования
def create_booking(db: Session, resident_id: int, spot_id: int, car_plate: str, start_time: datetime, end_time: datetime):
    booking = Booking(
        resident_id=resident_id,
        spot_id=spot_id,
        car_plate=car_plate,
        start_time=start_time,
        end_time=end_time
    )
    spot = db.query(ParkingSpot).filter_by(id=spot_id).first()
    if spot:
        spot.is_reserved = True
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking

# Отмена бронирования
def cancel_booking(db: Session, booking_id: int):
    booking = db.query(Booking).filter_by(id=booking_id).first()
    if booking:
        spot = db.query(ParkingSpot).filter_by(id=booking.spot_id).first()
        if spot:
            spot.is_reserved = False
        db.delete(booking)
        db.commit()
    return booking

# Получение всех бронирований для жителя
def get_resident_bookings(db: Session, resident_id: int):
    return db.query(Booking).filter_by(resident_id=resident_id).all()