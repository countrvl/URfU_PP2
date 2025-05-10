from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.utils.database_utils import (
    create_resident, get_all_residents, update_resident, delete_resident,
    create_parking_spot, get_all_parking_spots, update_parking_spot, delete_parking_spot,
    create_resident_by_name, get_resident_by_tg_id
)
from app.db.database import SessionLocal

router = APIRouter(prefix="/parking", tags=["Модуль парковки"])

# Dependency для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/residents")
async def view_residents(db: Session = Depends(get_db)):
    """
    Просмотр всех жителей.
    """
    residents = get_all_residents(db)
    return {"residents": residents}

@router.post("/residents/register")
async def register_resident(tg_id: int, name: str, db: Session = Depends(get_db)):
    """
    Эндпоинт для регистрации жителя.
    """
    existing_resident = get_resident_by_tg_id(db, tg_id)
    if existing_resident:
        raise HTTPException(status_code=400, detail="Resident with this tg_id already exists")

    new_resident = create_resident_by_name(db, tg_id, name)
    return {"message": "Resident registered successfully", "id": new_resident.id}

@router.put("/residents/{tg_id}")
async def update_resident_name(tg_id: int, new_name: str, db: Session = Depends(get_db)):
    """
    Обновление имени жителя.
    """
    resident = update_resident(db, tg_id, new_name)
    if not resident:
        raise HTTPException(status_code=404, detail="Resident not found")
    return {"message": "Resident updated successfully", "resident": resident}

@router.delete("/residents/{tg_id}")
async def remove_resident(tg_id: int, db: Session = Depends(get_db)):
    """
    Удаление жителя.
    """
    resident = delete_resident(db, tg_id)
    if not resident:
        raise HTTPException(status_code=404, detail="Resident not found")
    return {"message": "Resident deleted successfully"}