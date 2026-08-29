"""Simple FastAPI Microservice Launcher script for Project FORESIGHT.

Run directly via:
    python run_api.py
"""

import sys
from pathlib import Path
import uvicorn

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure src/ is on python path
src_dir = Path(__file__).resolve().parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

def run():
    print("=" * 60)
    print("Launching Project FORESIGHT FastAPI Microservice...")
    print("Swagger Docs: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/health")
    print("=" * 60)
    uvicorn.run("foresight.api.main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    run()
