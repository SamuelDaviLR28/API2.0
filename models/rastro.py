from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import datetime

class Geo(BaseModel):
    lat: float
    long: float

class File(BaseModel):
    url: HttpUrl
    description: Optional[str]
    fileType: Optional[str]

class Vehicle(BaseModel):
    manufacturer: Optional[str]
    model: Optional[str]
    color: Optional[str]
    licensePlate: Optional[str]

class Driver(BaseModel):
    name: Optional[str]
    phone: Optional[str]
    driversLicense: Optional[str]
    document: Optional[str]
    vehicle: Optional[Vehicle]

class Event(BaseModel):
    eventCode: str
    description: str
    date: datetime
    address: Optional[str]
    number: Optional[str]
    city: Optional[str]
    state: Optional[str]
    geo: Optional[Geo]
    files: Optional[List[File]]
    driver: Optional[Driver]

class EventData(BaseModel):
    trackingNumber: Optional[str]
    orderId: Optional[str]
    nfKey: Optional[str]
    CourierId: Optional[int]
    additionalInfo: Optional[dict]
    events: List[Event]

class RastroEvent(BaseModel):
    eventsData: List[EventData]