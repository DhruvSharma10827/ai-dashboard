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
    # Running as compiled executable (PyInstaller)
    # When frozen, PyInstaller sets sys._MEIPASS to the temp extraction folder
    # The package should be bundled there via spec file configuration
    bundle_dir = Path(sys._MEIPASS)  # type: ignore[attr-defined]
    
    # Add the bundle directory to path (where ai_dashboard should be bundled)
    if str(bundle_dir) not in sys.path:
        sys.path.insert(0, str(bundle_dir))
    
    # Also check if src folder exists in bundle (for src layout)
    src_in_bundle = bundle_dir / "src"
    if src_in_bundle.exists() and str(src_in_bundle.parent) not in sys.path:
        sys.path.insert(0, str(src_in_bundle.parent))
else:
    # Running in development mode - add src directory to path
    src_path = Path(__file__).parent / "src"
    if src_path.exists():
        sys.path.insert(0, str(src_path.parent))

from ai_dashboard.app import main

if __name__ == "__main__":
    main()
