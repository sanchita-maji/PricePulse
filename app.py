"""
PricePulse – Production Root Launcher & Public Hosting Entrypoint.

Allows the application to be deployed seamlessly across any hosting platform:
- Streamlit Community Cloud: can target either `app.py` or `frontend/app.py`
- Heroku / Render / Railway: `streamlit run frontend/app.py` or `python app.py`
- Container / Docker: `python app.py` or `streamlit run frontend/app.py`
- Direct Python execution: `python app.py`
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Load .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

_ROOT = Path(__file__).resolve().parent
_FRONTEND = _ROOT / "frontend"
_BACKEND = _ROOT / "backend"

for path_dir in (_ROOT, _FRONTEND, _BACKEND):
    if str(path_dir) not in sys.path:
        sys.path.insert(0, str(path_dir))

# Check if currently executing within Streamlit runtime
_is_streamlit = False
try:
    import streamlit as st
    if hasattr(st, "runtime") and st.runtime.exists():
        _is_streamlit = True
except Exception:
    pass

if _is_streamlit:
    # Invoked via `streamlit run app.py`
    import runpy
    runpy.run_path(str(_FRONTEND / "app.py"), run_name="__main__")
else:
    # Invoked via `python app.py`
    import streamlit.web.cli as stcli

    port = os.getenv("PORT", os.getenv("STREAMLIT_SERVER_PORT", "8501"))
    host = os.getenv("HOST", os.getenv("STREAMLIT_SERVER_ADDRESS", "0.0.0.0"))
    headless = os.getenv("STREAMLIT_SERVER_HEADLESS", "true").lower() in ("true", "1", "yes")

    frontend_entry = str(_FRONTEND / "app.py")

    args = [
        "streamlit",
        "run",
        frontend_entry,
        f"--server.port={port}",
        f"--server.address={host}",
        f"--server.headless={'true' if headless else 'false'}",
        "--browser.gatherUsageStats=false",
    ]
    # Pass any extra CLI arguments through
    if len(sys.argv) > 1:
        args.extend(sys.argv[1:])

    sys.argv = args
    sys.exit(stcli.main())
