from fastapi import FastAPI
from app.db.database import init_db
from app.controllers.ml_controller import router as ml_router
from app.controllers.booking_controller import router as booking_router
from app.controllers.parking_controller import router as parking_router

app = FastAPI(
    title="Parking Management System API",
    description="This is a simple API for managing parking reservations and residents.",
    version="1.0.0",
    docs_url="/swagger",
)

@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(ml_router)
app.include_router(booking_router)
app.include_router(parking_router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Parking Management System!"}