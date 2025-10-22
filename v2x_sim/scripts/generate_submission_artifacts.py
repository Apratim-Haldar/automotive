from __future__ import annotations
import os
import sys
import json
import csv
import time
import argparse
from pathlib import Path

# Ensure project root on path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.v2x_sim.simulation import Simulation
from main import build_scenario


def run_and_collect(
    duration: float = 60.0,
    dt: float = 0.1,
    ew_count: int = 6,
    ns_count: int = 6,
    spawn_gap_ew: float = 2.5,
    spawn_gap_ns: float = 2.2,
    v_ew: float = 12.0,
    v_ns: float = 11.0,
    seed: int = 42,
    signal_params: dict | None = None,
):
    sim = Simulation(dt=dt, signal_params=signal_params)
    build_scenario(
        sim,
        ew_count=ew_count,
        ns_count=ns_count,
        spawn_gap_ew=spawn_gap_ew,
        spawn_gap_ns=spawn_gap_ns,
        v_ew=v_ew,
        v_ns=v_ns,
        seed=seed,
    )

    timeline = []
    exited_over_time = []

    steps = int(duration / dt)
    for _ in range(steps):
        sim.step()
        # Record signal state and basic counts each tick
        approaching = sim.road.get_approaching_by_lane(sim.vehicles, radius=120.0)
        timeline.append({
            "t": round(sim.t, 2),
            "signal_state": sim.signal.state,
            "EW_approaching": len(approaching.get("EW", [])),
            "NS_approaching": len(approaching.get("NS", [])),
        })
        exited_over_time.append({
            "t": round(sim.t, 2),
            "vehicles_exited": sim.metrics.total_vehicles_exited,
        })

    return sim, timeline, exited_over_time


def write_artifacts(out_dir: Path, sim: Simulation, timeline, exited_over_time, config: dict):
    out_dir.mkdir(parents=True, exist_ok=True)

    # Metrics JSON
    metrics_path = out_dir / "metrics.json"
    with metrics_path.open("w", encoding="utf-8") as f:
        json.dump({
            "time": sim.t,
            "collisions": sim.metrics.collisions,
            "near_misses": sim.metrics.near_misses,
            "vehicles_exited": sim.metrics.total_vehicles_exited,
            "total_delay": sim.metrics.total_delay,
        }, f, indent=2)

    # Signal timeline CSV
    timeline_path = out_dir / "signal_timeline.csv"
    with timeline_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["t", "signal_state", "EW_approaching", "NS_approaching"])
        writer.writeheader()
        writer.writerows(timeline)

    # Exited over time CSV
    exited_path = out_dir / "vehicles_exited_over_time.csv"
    with exited_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["t", "vehicles_exited"])
        writer.writeheader()
        writer.writerows(exited_over_time)

    # Basic run log
    log_path = out_dir / "run_log.txt"
    with log_path.open("w", encoding="utf-8") as f:
        f.write("--- Simulation Complete ---\n")
        f.write(f"Time: {sim.t:.1f}s | Vehicles exited: {sim.metrics.total_vehicles_exited}\n")
        f.write(f"Collisions: {sim.metrics.collisions} | Near-misses: {sim.metrics.near_misses}\n")
        f.write(f"Total delay: {sim.metrics.total_delay:.2f}\n")

    # Config JSON
    cfg_path = out_dir / "config_used.json"
    with cfg_path.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate submission artifacts for V2X simulation")
    parser.add_argument("--duration", type=float, default=60.0)
    parser.add_argument("--dt", type=float, default=0.1)
    parser.add_argument("--ew-count", type=int, default=6)
    parser.add_argument("--ns-count", type=int, default=6)
    parser.add_argument("--spawn-gap-ew", type=float, default=2.5)
    parser.add_argument("--spawn-gap-ns", type=float, default=2.2)
    parser.add_argument("--v-ew", type=float, default=12.0)
    parser.add_argument("--v-ns", type=float, default=11.0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--min-green", type=float, default=8.0)
    parser.add_argument("--max-green", type=float, default=25.0)
    parser.add_argument("--yellow", type=float, default=3.0)
    parser.add_argument("--all-red", type=float, default=1.0)
    parser.add_argument("--tag", type=str, default="", help="Optional tag to append to artifacts folder name")

    args = parser.parse_args()

    ts = time.strftime("%Y%m%d_%H%M%S")
    folder = ts + (f"_{args.tag}" if args.tag else "")
    artifacts_dir = ROOT / "artifacts" / folder

    signal_params = {
        "min_green": args.min_green,
        "max_green": args.max_green,
        "yellow": args.yellow,
        "all_red": args.all_red,
    }

    sim, timeline, exited = run_and_collect(
        duration=args.duration,
        dt=args.dt,
        ew_count=args.ew_count,
        ns_count=args.ns_count,
        spawn_gap_ew=args.spawn_gap_ew,
        spawn_gap_ns=args.spawn_gap_ns,
        v_ew=args.v_ew,
        v_ns=args.v_ns,
        seed=args.seed,
        signal_params=signal_params,
    )

    cfg = {
        "duration": args.duration,
        "dt": args.dt,
        "ew_count": args.ew_count,
        "ns_count": args.ns_count,
        "spawn_gap_ew": args.spawn_gap_ew,
        "spawn_gap_ns": args.spawn_gap_ns,
        "v_ew": args.v_ew,
        "v_ns": args.v_ns,
        "seed": args.seed,
        "signal": signal_params,
    }
    write_artifacts(artifacts_dir, sim, timeline, exited, cfg)
    print(f"Artifacts written to: {artifacts_dir}")
