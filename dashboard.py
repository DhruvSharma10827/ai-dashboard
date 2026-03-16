#!/usr/bin/env python3
"""AI Dashboard - Enterprise AI Orchestration System.

A professional TUI for managing AI models, agents, and workflows.

This is the main entry point that maintains backward compatibility.
The actual application code is in the ai_dashboard package.

Usage:
    python dashboard.py
    ai-dashboard (if installed via pip)
"""

from ai_dashboard.app import main

if __name__ == "__main__":
    main()
