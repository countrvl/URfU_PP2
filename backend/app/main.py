from fastapi import FastAPI
from ultralytics import YOLO
from app.db.database import init_db
from app.controllers.ml_controller import router as ml_router
from app.controllers.booking_controller import router as booking_router
from app.controllers.parking_controller import router as parking_router

app = FastAPI(
    title="Система распознавания автомобильных номеров",
    version="1.0.0",
    docs_url="/swagger",
)

@app.on_event("startup")
def on_startup():
    init_db()
    global model
    model = YOLO('./ml/runs/detect/train/weights/best.pt')


app.include_router(ml_router)
app.include_router(booking_router)
app.include_router(parking_router)

@app.get("/")
async def root():
    return {"message": "Система распознавания автомобильных номеров"}