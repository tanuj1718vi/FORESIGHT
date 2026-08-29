"""Unified CLI & Application Entrypoint for Project FORESIGHT.

Usage:
    python main.py dashboard    # Launch Streamlit Decision Dashboard (:8501)
    python main.py api          # Launch FastAPI REST Microservice (:8000)
    python main.py pipeline     # Run complete End-to-End Data & ML Pipeline
    python main.py verify       # Run 15-Point Master Smoke Verification Battery
    python main.py test         # Run full Pytest Test Suite
"""

import sys
import subprocess
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def print_help():
    print("""
======================================================================
PROJECT FORESIGHT - Unified CLI Commands
======================================================================

  python main.py dashboard   -> Start interactive Streamlit dashboard (port 8501)
  python main.py api         -> Start FastAPI REST service (port 8000)
  python main.py pipeline    -> Re-run complete Data & ML pipeline
  python main.py verify      -> Run 15-point End-to-End verification battery
  python main.py test        -> Run all automated test suites

Quick Launchers:
  python run_dashboard.py    -> Quick dashboard start
  python run_api.py          -> Quick API service start
  python run_pipeline.py     -> Quick pipeline run
======================================================================
""")

def main():
    if len(sys.argv) < 2:
        print_help()
        import run_dashboard
        run_dashboard.run()
        return

    cmd = sys.argv[1].lower()

    if cmd in ["dashboard", "ui", "web"]:
        import run_dashboard
        run_dashboard.run()

    elif cmd in ["api", "server", "rest"]:
        import run_api
        run_api.run()

    elif cmd in ["pipeline", "train", "run"]:
        import run_pipeline
        run_pipeline.run_all()

    elif cmd in ["verify", "smoke"]:
        from scripts.e2e_verification import run_e2e_verification
        success = run_e2e_verification()
        sys.exit(0 if success else 1)

    elif cmd in ["test", "tests", "pytest"]:
        subprocess.run([sys.executable, "-m", "pytest", "-v"])

    else:
        print(f"Unknown command: '{cmd}'")
        print_help()

if __name__ == "__main__":
    main()
