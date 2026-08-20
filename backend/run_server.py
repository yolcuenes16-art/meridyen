"""Local development launcher that also supports Codex's bundled Python runtime."""
from pathlib import Path
import sys

_project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_project_root))

runtime_packages = Path(__file__).parent / ".runtime"
if runtime_packages.is_dir():
    sys.path.insert(0, str(runtime_packages))

import uvicorn

uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000)
