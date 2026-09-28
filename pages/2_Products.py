import runpy
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
for _p in (_ROOT, _ROOT / "frontend", _ROOT / "backend"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

runpy.run_path(str(_ROOT / "frontend" / "pages" / "2_Products.py"), run_name="__main__")
