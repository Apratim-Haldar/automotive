# V2X Traffic Safety System Simulation

Simulates multiple vehicles using V2V (vehicle-to-vehicle) and V2I (vehicle-to-infrastructure) communication to avoid collisions and optimize traffic signals.

- Language: Python 3.9+
- No external dependencies required
- Discrete-time simulation of two perpendicular approaches at a signalized intersection

## Quick start

1. Run the built-in scenario (defaults shown):

```powershell
# Default run (60s, dt=0.1, 6 cars each approach)
python .\main.py

# Control parameters
python .\main.py --duration 90 --dt 0.05 --ew-count 8 --ns-count 10 --spawn-gap-ew 2.0 --spawn-gap-ns 1.8 --v-ew 13 --v-ns 12 --min-green 6 --max-green 20 --yellow 3 --all-red 1
```

2. Run tests:

```powershell
python -m unittest -q
# Run a single test module
python -m unittest tests.test_collision_avoidance -q
```

3. Generate submission artifacts (metrics + CSV timelines):

```powershell
# Default
python .\scripts\generate_submission_artifacts.py

# With parameters and a folder tag
python .\scripts\generate_submission_artifacts.py --duration 90 --ew-count 10 --ns-count 10 --min-green 6 --max-green 18 --tag demo
```

4. One-command demo (runs tests, sim, artifacts):

```powershell
./scripts/run_demo.ps1
```

## Features
- V2V rear-end collision avoidance using predictive time-to-collision and safe headway.
- V2I cooperative signal approach: vehicles plan comfortable stops for reds.
- Adaptive traffic signal control extending green for approaching platoons and switching based on demand.
- Deterministic, reproducible scenario with metrics (collisions avoided, throughput, delay).

## Project structure
- `src/v2x_sim/models/` — Vehicle, Road, TrafficSignal.
- `src/v2x_sim/controllers/` — V2V and V2I controllers.
- `src/v2x_sim/` — Simulation engine.
- `tests/` — Unit tests for collision avoidance and signal optimization.
- `main.py` — Example scenario runner.

## Notes
- The road is modeled as two 1D approaches (EW and NS) crossing at an intersection. Vehicles move straight through.
- Vehicles broadcast state (position, speed) every tick; controllers remain lightweight and deterministic.

## Configuration
You can control most parameters via CLI flags, no code changes required:

- Simulation
	- `--duration` (s), `--dt` (s)
- Scenario
	- `--ew-count`, `--ns-count` (vehicles per approach)
	- `--spawn-gap-ew`, `--spawn-gap-ns` (s between spawns)
	- `--v-ew`, `--v-ns` (initial speed m/s)
	- `--seed` (random seed)
- Signal timings
	- `--min-green`, `--max-green`, `--yellow`, `--all-red` (seconds)

Artifacts script writes a `config_used.json` capturing all parameters of the run.

## Submission and demo
- What to submit:
	- The `v2x_sim` folder (or a Git repo link).
	- The generated `artifacts/` folder containing: `metrics.json`, `signal_timeline.csv`, `vehicles_exited_over_time.csv`, and `run_log.txt`.
	- A short PDF or README section summarizing: scenario, V2V logic, V2I logic, metrics and observations.
- How to demonstrate (suggested):
	1) Run tests to show correctness. 2) Run the scenario to print metrics. 3) Show `artifacts/` files and briefly explain the signal timeline and throughput. Optionally include a short screen recording.

For a detailed walkthrough with copy-paste commands, see `docs/GUIDE.md`.
