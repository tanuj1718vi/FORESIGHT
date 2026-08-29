"""Simple Dashboard Launcher script for Project FORESIGHT.

Run directly via:
    python run_dashboard.py
"""

import sys
import subprocess
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def run():
    print("=" * 60)
    print("Launching Project FORESIGHT Decision Intelligence Dashboard...")
    print("Open your browser at: http://localhost:8501")
    print("=" * 60)

    app_path = Path(__file__).resolve().parent / "app.py"
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(app_path), "--server.port=8501"])

if __name__ == "__main__":
    run()
