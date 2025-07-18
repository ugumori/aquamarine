from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Device(Base):
    __tablename__ = "devices"
    
    device_id = Column(String, primary_key=True)
    device_name = Column(String, nullable=False)
    gpio_number = Column(Integer, nullable=False, unique=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class Schedule(Base):
    __tablename__ = "schedules"
    
    schedule_id = Column(String, primary_key=True)
    device_id = Column(String, ForeignKey("devices.device_id"), nullable=False)
    schedule = Column(String, nullable=False)
    is_on = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())