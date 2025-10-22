import unittest

from src.v2x_sim.simulation import Simulation
from src.v2x_sim.models.vehicle import Vehicle


class TestSignalOptimization(unittest.TestCase):
    def test_signal_switches_to_demand(self):
        sim = Simulation(dt=0.1)
        # Start with EW green by default; create demand on NS only
        for i in range(6):
            v = Vehicle(id=100 + i, lane="NS", direction=+1, s=-100.0 - i * 12.0, v=8.0)
            sim.schedule_vehicle(0.0, v)

        # Run until after min green; verify signal eventually goes NS green
        saw_ns_green = False
        for _ in range(int(20.0 / sim.dt)):
            sim.step()
            if sim.signal.state == "NS_GREEN":
                saw_ns_green = True
                break
        self.assertTrue(saw_ns_green, "Signal did not switch to NS green under demand")


if __name__ == '__main__':
    unittest.main()
