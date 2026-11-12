"""Data models for College Bus Management System."""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class Bus(BaseModel):
    id: str
    plate_number: str
    capacity: int = Field(..., gt=0)
    driver_name: Optional[str] = None
    status: str = "ACTIVE"  # ACTIVE, MAINTENANCE, IN_TRANSIT


class BusRoute(BaseModel):
    id: str
    route_name: str
    origin: str
    destination: str
    stops: List[str]
    distance_km: float


class Passenger(BaseModel):
    id: str
    name: str
    role: str  # STUDENT, FACULTY
    bus_route_id: str
