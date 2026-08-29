"""Main Streamlit App Entrypoint for Project FORESIGHT.

Run directly via:
    streamlit run app.py
"""

import sys
from pathlib import Path

# Ensure src/ is on python path
src_dir = Path(__file__).resolve().parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from foresight.dashboard.app import main

main()
