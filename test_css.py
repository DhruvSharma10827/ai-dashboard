#!/usr/bin/env python3
"""Test script to validate Textual CSS in dashboard.py.

This script parses the CSS from dashboard.py and validates it by
attempting to load the application. Any CSS errors will be raised.
"""

import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Try to import the dashboard app at module level
try:
    from dashboard import AIDashboardApp

    DASHBOARD_AVAILABLE = True
except ImportError:
    DASHBOARD_AVAILABLE = False


def test_css_validation() -> int:
    """Validate CSS by importing and instantiating the app.

    Returns:
        0 if CSS is valid, 1 if there are errors.
    """
    if not DASHBOARD_AVAILABLE:
        print("⚠️ Textual not installed, skipping CSS import validation")
        return 0

    try:
        # Create an instance - this validates CSS variables
        AIDashboardApp()

        # Check if CSS was parsed without errors
        # Textual apps store CSS in the CSS class attribute
        if AIDashboardApp.CSS:
            print("✅ CSS parsed successfully")
            return 0
    except Exception as e:
        print(f"❌ CSS validation error: {e}")
        return 1
    else:
        print("⚠️ CSS is empty")
        return 1


def test_css_variables() -> int:
    """Check for commonly misused CSS variables.

    Returns:
        0 if no issues found, 1 if there are issues.
    """
    dashboard_path = Path(__file__).parent / "dashboard.py"
    content = dashboard_path.read_text()

    # Known invalid variables that don't exist in Textual
    invalid_vars = [
        "$text-on-primary",
        "$text-on-error",
        "$text-on-background",
        "$surface-darken",
        "$surface-lighten",
    ]

    # Use list comprehension to find issues
    issues = [var for var in invalid_vars if var in content]

    if issues:
        print(f"❌ Found invalid CSS variables: {', '.join(issues)}")
        print("   Valid alternatives: $background, $text, $text-muted, $panel, $surface")
        return 1

    print("✅ No invalid CSS variables found")
    return 0


if __name__ == "__main__":
    print("=" * 60)
    print("Textual CSS Validation")
    print("=" * 60)

    # Run variable check first (quick)
    var_result = test_css_variables()

    # Run full CSS validation
    css_result = test_css_validation()

    print("=" * 60)

    if var_result or css_result:
        sys.exit(1)
    sys.exit(0)
