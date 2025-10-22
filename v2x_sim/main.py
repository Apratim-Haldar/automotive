from __future__ import annotations
import random
import argparse

from src.v2x_sim.simulation import Simulation
from src.v2x_sim.models.vehicle import Vehicle


def build_scenario(
    sim: Simulation,
    ew_count: int = 6,
    ns_count: int = 6,
    spawn_gap_ew: float = 2.5,
    spawn_gap_ns: float = 2.2,
    ew_start_s: float = -220.0,
    ns_start_s: float = -200.0,
    spacing_ew: float = 25.0,
    spacing_ns: float = 22.0,
    v_ew: float = 12.0,
    v_ns: float = 11.0,
    v_jitter: float = 2.0,
    seed: int = 42,
):
    random.seed(seed)
    vid = 1
    # Spawn vehicles on EW
    t = 0.0
    for i in range(ew_count):
        v = Vehicle(
            id=vid,
            lane="EW",
            direction=+1,
            s=ew_start_s - i * spacing_ew,
            v=max(0.0, v_ew + (i % 3) - v_jitter * 0.0),
        )
        sim.schedule_vehicle(t, v)
        t += spawn_gap_ew
        vid += 1

    # Spawn vehicles on NS
    t = 1.0
    for i in range(ns_count):
        v = Vehicle(
            id=vid,
            lane="NS",
            direction=+1,
            s=ns_start_s - i * spacing_ns,
            v=max(0.0, v_ns + (i % 2) - v_jitter * 0.0),
        )
        sim.schedule_vehicle(t, v)
        t += spawn_gap_ns
        vid += 1


def main():
    parser = argparse.ArgumentParser(description="Run V2X simulation scenario")
    parser.add_argument("--duration", type=float, default=60.0, help="Simulation duration (s)")
    parser.add_argument("--dt", type=float, default=0.1, help="Timestep (s)")
    parser.add_argument("--ew-count", type=int, default=6, help="Vehicles on EW approach")
    parser.add_argument("--ns-count", type=int, default=6, help="Vehicles on NS approach")
    parser.add_argument("--spawn-gap-ew", type=float, default=2.5, help="Spawn interval EW (s)")
    parser.add_argument("--spawn-gap-ns", type=float, default=2.2, help="Spawn interval NS (s)")
    parser.add_argument("--v-ew", type=float, default=12.0, help="Initial speed EW (m/s)")
    parser.add_argument("--v-ns", type=float, default=11.0, help="Initial speed NS (m/s)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--min-green", type=float, default=8.0, help="Signal min green (s)")
    parser.add_argument("--max-green", type=float, default=25.0, help="Signal max green (s)")
    parser.add_argument("--yellow", type=float, default=3.0, help="Signal yellow (s)")
    parser.add_argument("--all-red", type=float, default=1.0, help="Signal all-red (s)")

    args = parser.parse_args()

    sim = Simulation(
        dt=args.dt,
        signal_params={
            "min_green": args.min_green,
            "max_green": args.max_green,
            "yellow": args.yellow,
            "all_red": args.all_red,
        },
    )
    build_scenario(
        sim,
        ew_count=args.ew_count,
        ns_count=args.ns_count,
        spawn_gap_ew=args.spawn_gap_ew,
        spawn_gap_ns=args.spawn_gap_ns,
        v_ew=args.v_ew,
        v_ns=args.v_ns,
        seed=args.seed,
    )

    metrics = sim.run(args.duration)

    print("--- Simulation Complete ---")
    print(f"Time: {sim.t:.1f}s | Vehicles exited: {metrics.total_vehicles_exited}")
    print(f"Collisions: {metrics.collisions} | Near-misses: {metrics.near_misses}")
    print(f"Total delay (veh*m/s*s): {metrics.total_delay:.2f}")


if __name__ == "__main__":
    main()
