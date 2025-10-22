import unittest

from src.v2x_sim.simulation import Simulation
from src.v2x_sim.models.vehicle import Vehicle


class TestCollisionAvoidance(unittest.TestCase):
    def test_follower_avoids_lead(self):
        sim = Simulation(dt=0.05)

        lead = Vehicle(id=1, lane="EW", direction=+1, s=-80.0, v=10.0)
        follower = Vehicle(id=2, lane="EW", direction=+1, s=-110.0, v=15.0)
        sim.schedule_vehicle(0.0, lead)
        sim.schedule_vehicle(0.0, follower)

        min_gap = float("inf")
        for _ in range(int(20.0 / sim.dt)):
            # manually measure gap before step
            gap = follower.direction * (lead.s - follower.s) - 0.5 * (lead.length + follower.length)
            if gap < min_gap:
                min_gap = gap
            sim.step()

        self.assertGreater(min_gap, 1.5, f"Too small min gap: {min_gap}")
        self.assertEqual(sim.metrics.collisions, 0, "Collision occurred unexpectedly")


if __name__ == '__main__':
    unittest.main()
