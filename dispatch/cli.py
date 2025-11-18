"""Command line interface for the dispatch system."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .models import Driver, TripRequest, Vehicle
from .service import DispatchSystem


def _parse_location(value: str) -> tuple[float, float]:
    try:
        lat, lng = value.split(",")
        return float(lat), float(lng)
    except Exception as exc:  # pragma: no cover - defensive
        raise argparse.ArgumentTypeError("Location must be in 'lat,lng' format") from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Lightweight dispatch system")
    parser.add_argument(
        "--storage",
        type=Path,
        default=Path("data/dispatch.json"),
        help="Path to the JSON storage file",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    vehicle = subparsers.add_parser("add-vehicle", help="Register a new vehicle")
    vehicle.add_argument("vehicle_id")
    vehicle.add_argument("capacity", type=int)
    vehicle.add_argument("location", type=_parse_location)

    driver = subparsers.add_parser("add-driver", help="Register a new driver")
    driver.add_argument("driver_id")
    driver.add_argument("name")
    driver.add_argument("vehicle_id")

    req = subparsers.add_parser("request", help="Create a trip request")
    req.add_argument("request_id")
    req.add_argument("passengers", type=int)
    req.add_argument("pickup", type=_parse_location)
    req.add_argument("dropoff", type=_parse_location)

    dispatch = subparsers.add_parser("dispatch", help="Assign a driver to a request")
    dispatch.add_argument("request_id")

    subparsers.add_parser("list-vehicles", help="List vehicles")
    subparsers.add_parser("list-drivers", help="List drivers")
    subparsers.add_parser("list-trips", help="List trip requests")

    return parser


def handle(args: argparse.Namespace) -> Any:
    system = DispatchSystem(args.storage)

    if args.command == "add-vehicle":
        system.register_vehicle(
            Vehicle(vehicle_id=args.vehicle_id, capacity=args.capacity, location=args.location)
        )
        return {"status": "ok"}

    if args.command == "add-driver":
        system.register_driver(
            Driver(driver_id=args.driver_id, name=args.name, vehicle_id=args.vehicle_id)
        )
        return {"status": "ok"}

    if args.command == "request":
        system.create_request(
            TripRequest(
                request_id=args.request_id,
                passengers=args.passengers,
                pickup=args.pickup,
                dropoff=args.dropoff,
            )
        )
        return {"status": "ok"}

    if args.command == "dispatch":
        summary = system.dispatch(args.request_id)
        return {
            "status": "assigned",
            "request": summary.request_id,
            "driver": summary.driver_id,
            "vehicle": summary.vehicle_id,
            "distance": round(summary.distance, 2),
        }

    if args.command == "list-vehicles":
        return [vehicle.__dict__ for vehicle in system.list_vehicles()]

    if args.command == "list-drivers":
        return [driver.__dict__ for driver in system.list_drivers()]

    if args.command == "list-trips":
        trips = []
        for trip in system.list_trips():
            data = trip.__dict__.copy()
            data["requested_at"] = trip.requested_at.isoformat()
            trips.append(data)
        return trips

    raise RuntimeError(f"Unsupported command: {args.command}")


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    output = handle(args)
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":  # pragma: no cover
    main()
