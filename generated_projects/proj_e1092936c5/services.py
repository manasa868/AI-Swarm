"""Bus Fleet and Route Service Logic."""
from typing import Dict, List, Optional
from models import Bus, BusRoute, Passenger


class BusManagementService:
    def __init__(self):
        self.buses: Dict[str, Bus] = {}
        self.routes: Dict[str, BusRoute] = {}
        self.passengers: Dict[str, Passenger] = {}

    def register_bus(self, bus_id: str, plate: str, capacity: int) -> Bus:
        bus = Bus(id=bus_id, plate_number=plate, capacity=capacity)
        self.buses[bus_id] = bus
        return bus

    def create_route(self, route_id: str, name: str, origin: str, dest: str, stops: List[str], distance: float) -> BusRoute:
        if distance <= 0:
            raise ValueError("Route distance must be positive")
        route = BusRoute(id=route_id, route_name=name, origin=origin, destination=dest, stops=stops, distance_km=distance)
        self.routes[route_id] = route
        return route

    def assign_driver(self, bus_id: str, driver_name: str) -> Bus:
        if bus_id not in self.buses:
            raise KeyError("Bus not found")
        self.buses[bus_id].driver_name = driver_name
        return self.buses[bus_id]
