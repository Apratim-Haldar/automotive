from __future__ import annotations

from ..models.vehicle import Vehicle
from ..models.traffic_signal import TrafficSignal
from ..models.road import Road


def v2i_signal_accel(v: Vehicle, sig: TrafficSignal, road: Road) -> float:
    """Compute additional accel command due to traffic signal state.
    - If red for lane: brake comfortably to stop line.
    - If yellow for lane: begin braking depending on distance.
    - If green: no extra effect.
    """
    if sig.is_red_for(v.lane):
        # Plan stop at stop line
        return v.comfortable_brake_to_stop()

    if sig.is_yellow_for(v.lane):
        # More conservative braking when close to stop line
        d = v.distance_to_stop_line()
        if d < 30.0:
            return min(0.0, v.comfortable_brake_to_stop())
        return 0.0

    # Green
    return 0.0
