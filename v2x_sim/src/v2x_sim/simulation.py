from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple

from .models.vehicle import Vehicle
from .models.road import Road
from .models.traffic_signal import TrafficSignal
from .controllers.v2v import v2v_rear_end_accel
from .controllers.v2i import v2i_signal_accel


@dataclass
class Metrics:
    collisions: int = 0
    near_misses: int = 0
    total_vehicles_exited: int = 0
    total_delay: float = 0.0  # sum of (v_des - v)+ per-vehicle over time


class Simulation:
    def __init__(self, dt: float = 0.1, signal_params: Optional[dict] = None):
        self.t: float = 0.0
        self.dt: float = dt
        self.road = Road()
        self.vehicles: List[Vehicle] = []
        if signal_params is None:
            self.signal = TrafficSignal(min_green=8.0, max_green=25.0, yellow=3.0, all_red=1.0)
        else:
            self.signal = TrafficSignal(**signal_params)
        self.metrics = Metrics()
        self._spawn_queue: List[Tuple[float, Vehicle]] = []  # (spawn_time, vehicle)

    def schedule_vehicle(self, spawn_time: float, vehicle: Vehicle) -> None:
        self._spawn_queue.append((spawn_time, vehicle))
        self._spawn_queue.sort(key=lambda x: x[0])

    def _spawn_due(self) -> None:
        while self._spawn_queue and self._spawn_queue[0][0] <= self.t:
            _, v = self._spawn_queue.pop(0)
            self.vehicles.append(v)

    def step(self) -> None:
        dt = self.dt
        self._spawn_due()

        # V2I: signal optimization using approaching info
        approaching = self.road.get_approaching_by_lane(self.vehicles, radius=120.0)
        self.signal.update(dt, approaching)

        # Compute controls for each vehicle
        for v in self.vehicles:
            # Base desire to reach v_des
            a_cmd = v.base_speed_control()

            # V2I: stopping for red / proceed for green
            a_cmd += v2i_signal_accel(v, self.signal, self.road)

            # V2V: rear-end safety in same lane
            lead = self.road.get_lead_vehicle(self.vehicles, v)
            a_cmd += v2v_rear_end_accel(v, lead)

            v.apply_control(a_cmd)

        # Integrate dynamics and collect metrics
        for i, v in enumerate(list(self.vehicles)):
            prev_v = v.v
            v.update(dt)

            # Delay metric (only positive when under v_des)
            self.metrics.total_delay += max(0.0, v.v_des - v.v) * dt

            # Intersection conflict check (near-miss tracking)
            if self.road.in_conflict_zone(v):
                for u in self.vehicles:
                    if u is v:
                        continue
                    if self.road.in_conflict_zone(u):
                        if abs(v.t_to_conflict() - u.t_to_conflict()) < 1.0:
                            self.metrics.near_misses += 1
                            break

            # Remove vehicles that have exited
            if self.road.exited(v):
                self.vehicles.pop(i)
                self.metrics.total_vehicles_exited += 1

        # Collision detection (rear-end in lane)
        for v in self.vehicles:
            lead = self.road.get_lead_vehicle(self.vehicles, v)
            if lead and (lead.s - v.s) < (v.length * 0.5 + lead.length * 0.5 + 0.5):
                self.metrics.collisions += 1

        self.t += dt

    def run(self, duration: float) -> Metrics:
        steps = int(duration / self.dt)
        for _ in range(steps):
            self.step()
        return self.metrics
