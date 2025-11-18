"""Simple JSON storage for the dispatch system."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable

from .models import Driver, TripRequest, Vehicle


class Storage:
    """Persist state to a JSON file."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> Dict[str, Dict[str, dict]]:
        if not self.path.exists():
            return {"vehicles": {}, "drivers": {}, "trips": {}}
        raw = json.loads(self.path.read_text())
        return raw

    def save(
        self,
        vehicles: Iterable[Vehicle],
        drivers: Iterable[Driver],
        trips: Iterable[TripRequest],
    ) -> None:
        payload = {
            "vehicles": {v.vehicle_id: asdict(v) for v in vehicles},
            "drivers": {d.driver_id: asdict(d) for d in drivers},
            "trips": {
                t.request_id: {
                    **asdict(t),
                    "requested_at": t.requested_at.isoformat(),
                }
                for t in trips
            },
        }
        self.path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))

    def load_models(self) -> tuple[Dict[str, Vehicle], Dict[str, Driver], Dict[str, TripRequest]]:
        payload = self.load()
        vehicles = {
            vid: Vehicle(**data)
            for vid, data in payload.get("vehicles", {}).items()
        }
        drivers = {
            did: Driver(**data)
            for did, data in payload.get("drivers", {}).items()
        }
        trips = {
            tid: TripRequest(
                **{
                    **data,
                    "requested_at": datetime.fromisoformat(data["requested_at"])
                    if isinstance(data.get("requested_at"), str)
                    else data.get("requested_at"),
                }
            )
            for tid, data in payload.get("trips", {}).items()
        }
        return vehicles, drivers, trips
