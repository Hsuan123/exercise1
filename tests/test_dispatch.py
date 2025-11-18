from pathlib import Path

from dispatch.models import Driver, TripRequest, Vehicle
from dispatch.service import DispatchSystem


def create_system(tmp_path: Path) -> DispatchSystem:
    return DispatchSystem(tmp_path / "dispatch.json")


def test_register_and_dispatch(tmp_path):
    system = create_system(tmp_path)
    system.register_vehicle(Vehicle("v1", capacity=4, location=(1, 1)))
    system.register_vehicle(Vehicle("v2", capacity=2, location=(2, 2)))
    system.register_driver(Driver("d1", "Alice", "v1"))
    system.register_driver(Driver("d2", "Bob", "v2"))

    system.create_request(
        TripRequest("r1", passengers=3, pickup=(0, 0), dropoff=(3, 3))
    )
    summary = system.dispatch("r1")
    assert summary.driver_id == "d1"
    assert summary.vehicle_id == "v1"


def test_dispatch_requires_capacity(tmp_path):
    system = create_system(tmp_path)
    system.register_vehicle(Vehicle("v1", capacity=2, location=(1, 1)))
    system.register_driver(Driver("d1", "Alice", "v1"))
    system.create_request(
        TripRequest("r1", passengers=3, pickup=(0, 0), dropoff=(1, 1))
    )

    try:
        system.dispatch("r1")
    except RuntimeError as exc:
        assert "No available drivers" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Dispatch should have failed")
