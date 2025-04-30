from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.utils.database_utils import (
    create_resident, get_all_residents, update_resident, delete_resident,
    create_parking_spot, get_all_parking_spots, update_parking_spot, delete_parking_spot
)
from app.db.database import SessionLocal

router = APIRouter(prefix="/parking", tags=["Parking Management"])

# Dependency для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CRUD для жителей
@router.post("/residents")
async def add_resident(name: str, db: Session = Depends(get_db)):
    """
    Добавление нового жителя.
    """
    resident = create_resident(db, name)
    return {"message": "Resident added successfully", "resident": resident}

@router.get("/residents")
async def view_residents(db: Session = Depends(get_db)):
    """
    Просмотр всех жителей.
    """
    residents = get_all_residents(db)
    return {"residents": residents}

@router.put("/residents/{resident_id}")
async def update_resident_name(resident_id: int, new_name: str, db: Session = Depends(get_db)):
    """
    Обновление имени жителя.
    """
    resident = update_resident(db, resident_id, new_name)
    if not resident:
        raise HTTPException(status_code=404, detail="Resident not found")
    return {"message": "Resident updated successfully", "resident": resident}

@router.delete("/residents/{resident_id}")
async def remove_resident(resident_id: int, db: Session = Depends(get_db)):
    """
    Удаление жителя.
    """
    resident = delete_resident(db, resident_id)
    if not resident:
        raise HTTPException(status_code=404, detail="Resident not found")
    return {"message": "Resident deleted successfully"}

# CRUD для парковочных мест
@router.post("/parking-spots")
async def add_parking_spot(parking_spot_number: str, description: str, db: Session = Depends(get_db)):
    """
    Добавление нового парковочного места.
    """
    spot = create_parking_spot(db, parking_spot_number, description)
    return {"message": "Parking spot added successfully", "spot": spot}

@router.get("/parking-spots")
async def view_parking_spots(db: Session = Depends(get_db)):
    """
    Просмотр всех парковочных мест.
    """
    spots = get_all_parking_spots(db)
    return {"parking_spots": spots}

@router.put("/parking-spots/{spot_id}")
async def update_parking_spot_description(spot_id: int, new_description: str, db: Session = Depends(get_db)):
    """
    Обновление описания парковочного места.
    """
    spot = update_parking_spot(db, spot_id, new_description)
    if not spot:
        raise HTTPException(status_code=404, detail="Parking spot not found")
    return {"message": "Parking spot updated successfully", "spot": spot}

@router.delete("/parking-spots/{spot_id}")
async def remove_parking_spot(spot_id: int, db: Session = Depends(get_db)):
    """
    Удаление парковочного места.
    """
    spot = delete_parking_spot(db, spot_id)
    if not spot:
        raise HTTPException(status_code=404, detail="Parking spot not found")
    return {"message": "Parking spot deleted successfully"}