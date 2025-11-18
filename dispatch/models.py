"""Core domain models for the dispatch system."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Tuple

Location = Tuple[float, float]


@dataclass
class Vehicle:
    vehicle_id: str
    capacity: int
    location: Location
    active: bool = True


@dataclass
class Driver:
    driver_id: str
    name: str
    vehicle_id: str
    available: bool = True


@dataclass
class TripRequest:
    request_id: str
    passengers: int
    pickup: Location
    dropoff: Location
    requested_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "pending"  # pending -> assigned -> completed -> cancelled
    assigned_vehicle_id: Optional[str] = None
    assigned_driver_id: Optional[str] = None

    def is_dispatchable(self) -> bool:
        """Return True if the trip has not been assigned or cancelled."""
        return self.status == "pending"

    def mark_assigned(self, vehicle_id: str, driver_id: str) -> None:
        self.assigned_vehicle_id = vehicle_id
        self.assigned_driver_id = driver_id
        self.status = "assigned"

    def mark_completed(self) -> None:
        self.status = "completed"

    def cancel(self) -> None:
        self.status = "cancelled"
