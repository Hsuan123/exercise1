"""Business logic for the dispatch system."""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from .models import Driver, Location, TripRequest, Vehicle
from .storage import Storage


@dataclass
class DispatchSummary:
    request_id: str
    driver_id: str
    vehicle_id: str
    distance: float


class DispatchSystem:
    def __init__(self, storage_path: Path) -> None:
        self.storage = Storage(storage_path)
        self.vehicles: Dict[str, Vehicle]
        self.drivers: Dict[str, Driver]
        self.trips: Dict[str, TripRequest]
        self._load()

    # ------------------------------------------------------------------
    # CRUD operations
    def _load(self) -> None:
        self.vehicles, self.drivers, self.trips = self.storage.load_models()

    def _persist(self) -> None:
        self.storage.save(self.vehicles.values(), self.drivers.values(), self.trips.values())

    def register_vehicle(self, vehicle: Vehicle) -> None:
        self.vehicles[vehicle.vehicle_id] = vehicle
        self._persist()

    def register_driver(self, driver: Driver) -> None:
        if driver.vehicle_id not in self.vehicles:
            raise ValueError(f"Vehicle {driver.vehicle_id} does not exist")
        self.drivers[driver.driver_id] = driver
        self._persist()

    def create_request(self, request: TripRequest) -> None:
        if request.passengers < 1:
            raise ValueError("A trip must have at least one passenger")
        self.trips[request.request_id] = request
        self._persist()

    def cancel_request(self, request_id: str) -> None:
        request = self.trips.get(request_id)
        if not request:
            raise KeyError(f"Unknown request {request_id}")
        request.cancel()
        self._persist()

    def complete_request(self, request_id: str) -> None:
        request = self.trips.get(request_id)
        if not request:
            raise KeyError(f"Unknown request {request_id}")
        request.mark_completed()
        self._persist()

    # ------------------------------------------------------------------
    # Dispatch logic
    def dispatch(self, request_id: str) -> DispatchSummary:
        request = self.trips.get(request_id)
        if not request:
            raise KeyError(f"Unknown request {request_id}")
        if not request.is_dispatchable():
            raise ValueError(f"Request {request_id} is not dispatchable (status={request.status})")

        candidates = self._eligible_drivers(request.passengers)
        if not candidates:
            raise RuntimeError("No available drivers with enough capacity")

        driver_id, vehicle_id, distance = min(
            candidates,
            key=lambda item: (item[2], item[0]),
        )

        request.mark_assigned(vehicle_id, driver_id)
        self.drivers[driver_id].available = False
        self._persist()
        return DispatchSummary(
            request_id=request_id,
            driver_id=driver_id,
            vehicle_id=vehicle_id,
            distance=distance,
        )

    def _eligible_drivers(self, passengers: int) -> List[tuple[str, str, float]]:
        candidates = []
        for driver in self.drivers.values():
            if not driver.available:
                continue
            vehicle = self.vehicles.get(driver.vehicle_id)
            if not vehicle or not vehicle.active:
                continue
            if vehicle.capacity < passengers:
                continue
            distance = math.dist(vehicle.location, (0.0, 0.0))
            candidates.append((driver.driver_id, vehicle.vehicle_id, distance))
        return candidates

    def update_vehicle_location(self, vehicle_id: str, location: Location) -> None:
        vehicle = self.vehicles.get(vehicle_id)
        if not vehicle:
            raise KeyError(f"Unknown vehicle {vehicle_id}")
        vehicle.location = location
        self._persist()

    def set_driver_availability(self, driver_id: str, available: bool) -> None:
        driver = self.drivers.get(driver_id)
        if not driver:
            raise KeyError(f"Unknown driver {driver_id}")
        driver.available = available
        self._persist()

    # Convenience helpers ------------------------------------------------
    def list_drivers(self) -> Iterable[Driver]:
        return sorted(self.drivers.values(), key=lambda d: d.driver_id)

    def list_vehicles(self) -> Iterable[Vehicle]:
        return sorted(self.vehicles.values(), key=lambda v: v.vehicle_id)

    def list_trips(self, status: Optional[str] = None) -> Iterable[TripRequest]:
        trips = self.trips.values()
        if status:
            trips = [t for t in trips if t.status == status]
        return sorted(trips, key=lambda t: t.requested_at)
