from datetime import datetime, UTC
from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Device(Base):
    __tablename__ = "devices"

    device_id = Column(String, primary_key=True)
    device_name = Column(String, nullable=False)
    gpio_number = Column(Integer, nullable=False, unique=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)) 
