from __future__ import annotations
from typing import Optional

from ..models.vehicle import Vehicle


def v2v_rear_end_accel(ego: Vehicle, lead: Optional[Vehicle]) -> float:
    """
    Predictive rear-end avoidance: if time-to-collision (TTC) within horizon, apply braking
    to keep a safe time headway and distance buffer.
    Returns an acceleration delta to be added to base speed control (negative for braking).
    """
    if not lead:
        return 0.0

    # Desired gap based on headway
    desired_gap = max(2.0, ego.v * ego.t_headway + 0.5 * (ego.length + lead.length))
    gap = ego.direction * (lead.s - ego.s) - 0.5 * (ego.length + lead.length)

    # If too close, brake proportional to gap error
    if gap < desired_gap:
        # Proportional braking with cap
        err = desired_gap - gap
        return -min(ego.d_max, 0.8 * err)

    # TTC-based early braking if closing in fast
    ttc = ego.ttc_with_lead(lead)
    if ttc < 2.0:
        return -min(ego.d_max * 0.7, (2.0 - ttc))

    return 0.0
