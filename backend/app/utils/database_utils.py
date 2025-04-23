from sqlalchemy.orm import Session
from app.db.models import Resident, ParkingSpot, Log

# Создание записи в таблице Residents
def create_resident(db: Session, name: str):
    resident = Resident(name=name)
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
def create_parking_spot(db: Session, description: str):
    spot = ParkingSpot(description=description, is_reserved=False)
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