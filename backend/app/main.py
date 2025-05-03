from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine, init_db
from app.db.models import Resident, ParkingSpot, Car
from app.utils.database_utils import (
    create_resident, get_all_residents, update_resident, delete_resident,
    create_parking_spot, get_all_parking_spots, update_parking_spot, delete_parking_spot,
    get_cars_by_tg_id
)
from app.controllers.ml_controller import router as ml_router
from app.controllers.booking_controller import router as booking_router
from app.controllers.parking_controller import router as parking_router

# Создание экземпляра FastAPI
app = FastAPI(
    title="Parking Management System API",
    description="This is a simple API for managing parking reservations and residents.",
    version="1.0.0",
    docs_url="/swagger",
)

# Подключение шаблонизатора Jinja2
templates = Jinja2Templates(directory="app/templates")

# Подключение статических файлов
app.mount("/static", StaticFiles(directory="app/static"), name="static")


# Dependency для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Инициализация базы данных при запуске приложения
@app.on_event("startup")
def on_startup():
    init_db()


# Главная страница
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    residents = get_all_residents(db)
    parking_spots = get_all_parking_spots(db)
    return templates.TemplateResponse("base.html",
                                      {"request": request, "residents": residents, "parking_spots": parking_spots})


# Страница администратора жителей
@app.get("/residents", response_class=HTMLResponse)
async def view_residents(request: Request, db: Session = Depends(get_db)):
    residents = get_all_residents(db)
    return templates.TemplateResponse("residents.html", {"request": request, "residents": residents})


# Страница добавления жителя
@app.get("/residents/add", response_class=HTMLResponse)
async def add_resident_form(request: Request):
    return templates.TemplateResponse("add_resident.html", {"request": request})


# Обработка формы добавления жителя
@app.post("/residents/add", response_class=HTMLResponse)
async def add_resident(request: Request, tg_id: int = Form(...), name: str = Form(...), db: Session = Depends(get_db)):
    existing_resident = db.query(Resident).filter_by(tg_id=tg_id).first()
    if existing_resident:
        return templates.TemplateResponse("add_resident.html",
                                          {"request": request, "error": "Resident with this tg_id already exists"})

    new_resident = create_resident(db, tg_id)
    return templates.TemplateResponse("add_resident.html",
                                      {"request": request, "message": "Resident added successfully",
                                       "resident": new_resident})


# Страница редактирования жителя
@app.get("/residents/{resident_id}/edit", response_class=HTMLResponse)
async def edit_resident_form(request: Request, resident_id: int, db: Session = Depends(get_db)):
    resident = db.query(Resident).filter_by(id=resident_id).first()
    if not resident:
        raise HTTPException(status_code=404, detail="Resident not found")
    return templates.TemplateResponse("edit_resident.html", {"request": request, "resident": resident})


# Обработка формы редактирования жителя
@app.post("/residents/{resident_id}/edit", response_class=HTMLResponse)
async def edit_resident(request: Request, resident_id: int, new_name: str = Form(...), db: Session = Depends(get_db)):
    resident = update_resident(db, resident_id, new_name)
    if not resident:
        raise HTTPException(status_code=404, detail="Resident not found")
    return templates.TemplateResponse("edit_resident.html",
                                      {"request": request, "message": "Resident updated successfully",
                                       "resident": resident})


# Удаление жителя
@app.post("/residents/{resident_id}/delete", response_class=HTMLResponse)
async def remove_resident(request: Request, resident_id: int, db: Session = Depends(get_db)):
    resident = delete_resident(db, resident_id)
    if not resident:
        raise HTTPException(status_code=404, detail="Resident not found")
    return templates.TemplateResponse("residents.html", {"request": request, "message": "Resident deleted successfully",
                                                         "residents": get_all_residents(db)})


# Страница администратора парковочных мест
@app.get("/parking-spots", response_class=HTMLResponse)
async def view_parking_spots(request: Request, db: Session = Depends(get_db)):
    parking_spots = get_all_parking_spots(db)
    return templates.TemplateResponse("parking_spots.html", {"request": request, "parking_spots": parking_spots})


# Страница добавления парковочного места
@app.get("/parking-spots/add", response_class=HTMLResponse)
async def add_parking_spot_form(request: Request):
    return templates.TemplateResponse("add_parking_spot.html", {"request": request})


# Обработка формы добавления парковочного места
@app.post("/parking-spots/add", response_class=HTMLResponse)
async def add_parking_spot(request: Request, parking_spot_number: str = Form(...), description: str = Form(...),
                           db: Session = Depends(get_db)):
    existing_spot = db.query(ParkingSpot).filter_by(parking_spot_number=parking_spot_number).first()
    if existing_spot:
        return templates.TemplateResponse("add_parking_spot.html",
                                          {"request": request, "error": "Parking spot with this number already exists"})

    new_spot = create_parking_spot(db, parking_spot_number, description)
    return templates.TemplateResponse("add_parking_spot.html",
                                      {"request": request, "message": "Parking spot added successfully",
                                       "spot": new_spot})


# Страница редактирования парковочного места
@app.get("/parking-spots/{spot_id}/edit", response_class=HTMLResponse)
async def edit_parking_spot_form(request: Request, spot_id: int, db: Session = Depends(get_db)):
    spot = db.query(ParkingSpot).filter_by(id=spot_id).first()
    if not spot:
        raise HTTPException(status_code=404, detail="Parking spot not found")
    return templates.TemplateResponse("edit_parking_spot.html", {"request": request, "spot": spot})


# Обработка формы редактирования парковочного места
@app.post("/parking-spots/{spot_id}/edit", response_class=HTMLResponse)
async def edit_parking_spot(request: Request, spot_id: int, new_description: str = Form(...),
                            db: Session = Depends(get_db)):
    spot = update_parking_spot(db, spot_id, new_description)
    if not spot:
        raise HTTPException(status_code=404, detail="Parking spot not found")
    return templates.TemplateResponse("edit_parking_spot.html",
                                      {"request": request, "message": "Parking spot updated successfully",
                                       "spot": spot})


# Удаление парковочного места
@app.post("/parking-spots/{spot_id}/delete", response_class=HTMLResponse)
async def remove_parking_spot(request: Request, spot_id: int, db: Session = Depends(get_db)):
    spot = delete_parking_spot(db, spot_id)
    if not spot:
        raise HTTPException(status_code=404, detail="Parking spot not found")
    return templates.TemplateResponse("parking_spots.html",
                                      {"request": request, "message": "Parking spot deleted successfully",
                                       "parking_spots": get_all_parking_spots(db)})


# Страница просмотра автомобилей для конкретного жителя
@app.get("/residents/{resident_id}/cars", response_class=HTMLResponse)
async def get_resident_cars(request: Request, resident_id: int, db: Session = Depends(get_db)):
    resident = db.query(Resident).filter_by(id=resident_id).first()
    if not resident:
        raise HTTPException(status_code=404, detail="Resident not found")

    cars = get_cars_by_tg_id(db, resident_id)
    return templates.TemplateResponse("cars.html", {"request": request, "resident": resident, "cars": cars})


# Включение существующих маршрутов для API
app.include_router(ml_router)
app.include_router(booking_router)
app.include_router(parking_router)