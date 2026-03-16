#!/usr/bin/env python3
"""AI Dashboard - Enterprise AI Orchestration System.

A professional TUI for managing AI models, agents, and workflows.

This is the main entry point that maintains backward compatibility.
The actual application code is in the ai_dashboard package.

Usage:
    python dashboard.py
    ai-dashboard (if installed via pip)
"""

import sys
from pathlib import Path

# Handle both development and PyInstaller frozen modes
if getattr(sys, "frozen", False):
    # Running as compiled executable
    bundle_dir = Path(sys._MEIPASS)  # type: ignore
    src_path = bundle_dir / "src"
    if src_path.exists():
        sys.path.insert(0, str(src_path))
else:
    # Running in development mode
    src_path = Path(__file__).parent / "src"
    if src_path.exists():
        sys.path.insert(0, str(src_path.parent))

from ai_dashboard.app import main

if __name__ == "__main__":
    main()
