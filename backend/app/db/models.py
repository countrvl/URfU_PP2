from sqlalchemy import Column, Integer, String, Boolean
from .database import Base

class Resident(Base):
    __tablename__ = "residents"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

class ParkingSpot(Base):
    __tablename__ = "parking_spots"
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, index=True)
    is_reserved = Column(Boolean, default=False)

class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index=True)
    message = Column(String, index=True)