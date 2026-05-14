"""
Data models for flight search and pricing
"""
from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field


class FlightProvider(str, Enum):
    """Supported flight booking providers"""
    SKYSCANNER = "skyscanner"
    KAYAK = "kayak"
    GOOGLE_FLIGHTS = "google_flights"
    EXPEDIA = "expedia"
    BOOKING = "booking"


class FlightSearch(BaseModel):
    """Flight search request"""
    origin: str = Field(..., description="IATA code (e.g., JFK)")
    destination: str = Field(..., description="IATA code (e.g., LAX)")
    departure_date: str = Field(..., description="YYYY-MM-DD format")
    return_date: Optional[str] = Field(None, description="YYYY-MM-DD format for round trip")
    passengers: int = Field(default=1, ge=1, le=9)
    cabin_class: str = Field(default="economy", description="economy, business, first")


class Flight(BaseModel):
    """Flight details"""
    id: str
    provider: FlightProvider
    provider_url: str
    origin: str
    destination: str
    departure: datetime
    arrival: datetime
    duration_minutes: int
    stops: int
    airline: str
    flight_number: str
    price: float
    currency: str = "USD"
    seat_available: int

    class Config:
        json_schema_extra = {
            "example": {
                "id": "flight_123",
                "provider": "skyscanner",
                "provider_url": "https://skyscanner.com/...",
                "origin": "JFK",
                "destination": "LAX",
                "departure": "2026-06-15T08:00:00",
                "arrival": "2026-06-15T11:30:00",
                "duration_minutes": 330,
                "stops": 0,
                "airline": "Delta Airlines",
                "flight_number": "DL123",
                "price": 245.99,
                "currency": "USD",
                "seat_available": 12
            }
        }


class FlightSearchResponse(BaseModel):
    """Response containing multiple flight options"""
    search_params: FlightSearch
    flights: list[Flight]
    total_results: int
    timestamp: datetime


class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    version: str = "1.0.0"


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime
