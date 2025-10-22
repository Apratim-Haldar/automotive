from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List

from .vehicle import Vehicle


@dataclass
class TrafficSignal:
    min_green: float = 8.0
    max_green: float = 25.0
    yellow: float = 3.0
    all_red: float = 1.0

    state: str = "EW_GREEN"  # EW_GREEN, EW_YELLOW, ALL_RED, NS_GREEN, NS_YELLOW
    t_in_state: float = 0.0

    def is_green_for(self, lane: str) -> bool:
        return (self.state == "EW_GREEN" and lane == "EW") or (self.state == "NS_GREEN" and lane == "NS")

    def is_yellow_for(self, lane: str) -> bool:
        return (self.state == "EW_YELLOW" and lane == "EW") or (self.state == "NS_YELLOW" and lane == "NS")

    def is_red_for(self, lane: str) -> bool:
        if self.state == "ALL_RED":
            return True
        if lane == "EW":
            return self.state in ("NS_GREEN", "NS_YELLOW")
        else:
            return self.state in ("EW_GREEN", "EW_YELLOW")

    def update(self, dt: float, approaching: Dict[str, List[Vehicle]]) -> None:
        self.t_in_state += dt

        # State machine timing
        if self.state in ("EW_GREEN", "NS_GREEN"):
            # Demand responsive green extension
            lane = "EW" if self.state == "EW_GREEN" else "NS"
            other = "NS" if lane == "EW" else "EW"
            lane_has_close = any(v.distance_to_stop_line() < 40.0 for v in approaching.get(lane, []))
            other_queue = len([v for v in approaching.get(other, []) if v.distance_to_stop_line() > 10.0])

            if self.t_in_state < self.min_green:
                return
            # If platoon approaching or queue still exists, extend up to max
            if lane_has_close and self.t_in_state < self.max_green:
                return
            # If other direction has clear demand and we've reached min, switch
            if other_queue > 0 or self.t_in_state >= self.max_green:
                self.state = ("EW_YELLOW" if lane == "EW" else "NS_YELLOW")
                self.t_in_state = 0.0
                return

        elif self.state in ("EW_YELLOW", "NS_YELLOW"):
            if self.t_in_state >= self.yellow:
                self.state = "ALL_RED"
                self.t_in_state = 0.0
                return

        elif self.state == "ALL_RED":
            if self.t_in_state >= self.all_red:
                # Switch to the opposite green
                self.state = "NS_GREEN" if self.previous_major() == "EW" else "EW_GREEN"
                self.t_in_state = 0.0
                return

    def previous_major(self) -> str:
        # Determines which was the last green based on current state
        if self.state in ("EW_GREEN", "EW_YELLOW"):
            return "EW"
        if self.state in ("NS_GREEN", "NS_YELLOW"):
            return "NS"
        # If all red, assume last was EW for deterministic choice
        return "EW"
