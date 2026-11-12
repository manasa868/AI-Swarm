"""Automated tests for Bus Management System."""
import unittest
from services import BusManagementService


class TestBusServices(unittest.TestCase):
    def setUp(self):
        self.service = BusManagementService()

    def test_bus_registration(self):
        bus = self.service.register_bus("BUS-01", "KA-01-AB-1234", 45)
        self.assertEqual(bus.capacity, 45)
        self.assertEqual(bus.status, "ACTIVE")

    def test_route_creation(self):
        route = self.service.create_route(
            "RT-101", "Campus Express", "Central Station", "College Campus",
            ["Stop A", "Stop B"], 14.5
        )
        self.assertEqual(route.route_name, "Campus Express")
        self.assertGreater(route.distance_km, 0, "Route distance must be positive")


if __name__ == "__main__":
    unittest.main()
