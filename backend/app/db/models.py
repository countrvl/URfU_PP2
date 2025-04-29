from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .database import Base

class Resident(Base):
    __tablename__ = "residents"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    tg_id = Column(Integer, unique=True, nullable=False)
    cars = relationship("Car", back_populates="owner")
    bookings = relationship("Booking", back_populates="resident")

class Car(Base):
    __tablename__ = "cars"
    id = Column(Integer, primary_key=True, index=True)
    car_plate = Column(String, unique=True, index=True, nullable=False)
    owner_id = Column(Integer, ForeignKey("residents.id"), nullable=False)
    owner = relationship("Resident", back_populates="cars")

class ParkingSpot(Base):
    __tablename__ = "parking_spots"
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, index=True)
    is_reserved = Column(Boolean, default=False)
    bookings = relationship("Booking", back_populates="spot")

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    resident_id = Column(Integer, ForeignKey("residents.id"), nullable=False)
    spot_id = Column(Integer, ForeignKey("parking_spots.id"), nullable=False)
    car_plate = Column(String, ForeignKey("cars.car_plate"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    resident = relationship("Resident", back_populates="bookings")
    spot = relationship("ParkingSpot", back_populates="bookings")

class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index=True)
    message = Column(String, index=True)