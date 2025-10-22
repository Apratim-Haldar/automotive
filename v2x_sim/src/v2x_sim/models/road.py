from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional

from .vehicle import Vehicle


@dataclass
class Road:
    # 1D approaches for EW and NS crossing at s=0
    exit_distance: float = 250.0  # vehicles removed if |s| > exit_distance
    conflict_half_width: float = 6.0  # meters around s=0 considered conflict zone

    def get_approaching_by_lane(self, vehicles: List[Vehicle], radius: float) -> Dict[str, List[Vehicle]]:
        res = {"EW": [], "NS": []}
        for v in vehicles:
            d = v.distance_to_stop_line()
            if 0.0 <= d <= radius:
                res[v.lane].append(v)
        # Sort by distance ascending (closest first)
        for k in res:
            res[k].sort(key=lambda x: x.distance_to_stop_line())
        return res

    def get_lead_vehicle(self, vehicles: List[Vehicle], ego: Vehicle) -> Optional[Vehicle]:
        best = None
        best_gap = float("inf")
        for v in vehicles:
            if v is ego:
                continue
            if v.lane != ego.lane or v.direction != ego.direction:
                continue
            # ahead if direction*(v.s - ego.s) > 0
            ahead = ego.direction * (v.s - ego.s) > 0
            if not ahead:
                continue
            gap = ego.direction * (v.s - ego.s)
            if gap < best_gap:
                best_gap = gap
                best = v
        return best

    def exited(self, v: Vehicle) -> bool:
        return abs(v.s) > self.exit_distance

    def in_conflict_zone(self, v: Vehicle) -> bool:
        return abs(v.s) <= self.conflict_half_width
