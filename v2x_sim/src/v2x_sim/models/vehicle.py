from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import math


@dataclass
class Vehicle:
    id: int
    lane: str  # 'EW' or 'NS'
    direction: int  # +1 moves to +s (toward +inf), -1 opposite; we use +1 toward intersection
    s: float  # longitudinal position along approach (m). Intersection at s=0.
    v: float  # m/s
    a: float = 0.0  # m/s^2
    length: float = 4.5
    v_des: float = 14.0  # desired speed (m/s ~ 50 km/h)
    a_max: float = 2.0  # comfortable accel
    d_max: float = 3.5  # comfortable braking (positive number)
    t_headway: float = 1.2  # desired time headway (s)
    comm_range: float = 200.0  # V2V/V2I range (m)

    def base_speed_control(self) -> float:
        # Simple P-control to reach v_des
        err = self.v_des - self.v
        a_cmd = 0.6 * err
        return max(-self.d_max, min(self.a_max, a_cmd))

    def apply_control(self, a_cmd: float) -> None:
        # Saturate
        self.a = max(-self.d_max, min(self.a_max, a_cmd))

    def update(self, dt: float) -> None:
        # Kinematic update with clamp
        self.v = max(0.0, self.v + self.a * dt)
        self.s += self.direction * self.v * dt

    def distance_to_stop_line(self) -> float:
        # Distance (signed) to intersection stop line at s=0
        return -self.direction * self.s

    def stopping_required(self, red: bool) -> bool:
        return red

    def comfortable_brake_to_stop(self) -> float:
        # Return braking to stop within remaining distance (if needed)
        d = max(0.0, self.distance_to_stop_line())
        if d < 1e-6:
            return -self.d_max
        # v^2 = 2 a d  => a = - v^2/(2d)
        a_needed = -(self.v ** 2) / (2.0 * d)
        return max(-self.d_max, a_needed)

    def ttc_with_lead(self, lead: Optional[Vehicle]) -> float:
        if not lead:
            return math.inf
        gap = self.direction * (lead.s - self.s) - 0.5 * (self.length + lead.length)
        rel_v = self.v - lead.v
        if gap <= 0:
            return 0.0
        if rel_v <= 0:
            return math.inf
        return gap / rel_v

    def t_to_conflict(self) -> float:
        # time to reach conflict zone center at s=0 (if moving toward it)
        if self.direction == 0 or self.v <= 1e-6:
            return math.inf
        d = self.distance_to_stop_line()
        if d < 0:
            return math.inf
        return d / self.v
