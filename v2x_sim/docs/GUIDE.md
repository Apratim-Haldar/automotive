# V2X Simulation: Quick Guide

This guide shows how to run tests, control scenario parameters (number of vehicles, spawn rates, timing), run the simulation, and generate submission artifacts on Windows PowerShell.

## Prerequisites
- Python 3.9+ (we tested with Python 3.13)
- On first use (optional, only if your environment is not yet set):
  - Create venv: `python -m venv .venv`
  - Activate: `.\.venv\Scripts\Activate.ps1`
  - Install deps: `pip install -r requirements.txt` (empty by default)

## Run tests
```powershell
# From v2x_sim folder
python -m unittest -q

# Run a single test module
python -m unittest tests.test_collision_avoidance -q
```

## Run the simulation (defaults)
```powershell
python .\main.py
```

## Customize the scenario
You can change most settings using CLI flags (no code changes required).

- Simulation
  - `--duration` (seconds), `--dt` (seconds)
- Vehicles
  - `--ew-count`, `--ns-count` (vehicles per approach)
  - `--spawn-gap-ew`, `--spawn-gap-ns` (seconds between spawns)
  - `--v-ew`, `--v-ns` (initial speeds, m/s)
  - `--seed` (random seed)
- Traffic signal timings
  - `--min-green`, `--max-green`, `--yellow`, `--all-red` (seconds)

Example:
```powershell
python .\main.py --duration 90 --dt 0.05 --ew-count 8 --ns-count 10 --spawn-gap-ew 2.0 --spawn-gap-ns 1.8 --v-ew 13 --v-ns 12 --min-green 6 --max-green 20 --yellow 3 --all-red 1
```

## One-command demo (PowerShell script)
Use `scripts\run_demo.ps1` to run tests, simulation, and artifacts in one go. You can override defaults with parameters.

```powershell
# Default demo
.\scripts\run_demo.ps1

# Demo with custom parameters
.\scripts\run_demo.ps1 -Duration 90 -Dt 0.05 -EWCount 8 -NSCount 10 -MinGreen 6 -MaxGreen 20 -Yellow 3 -AllRed 1 -Tag demo
```

## Notes
- No external dependencies are required. Everything runs with the Python standard library.
- The model is intentionally simple and deterministic to keep it explainable and easy to grade.
