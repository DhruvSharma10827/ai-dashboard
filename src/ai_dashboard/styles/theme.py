"""Theme and CSS styles for AI Dashboard.

This module provides comprehensive CSS styling with:
- Multiple theme support
- Consistent color schemes
- Responsive layouts
- Proper text visibility
- Professional UI components

Example:
    >>> css = get_theme_css("default")
"""

from __future__ import annotations

from typing import Literal

ThemeName = Literal["default", "dark", "light", "dracula", "nord"]


# Base CSS with all styles
CSS = """
/* ==========================================================================
   ROOT & GLOBAL STYLES
   ========================================================================== */

* {
    color: $text;
    text-opacity: 1;
}

Screen {
    background: $surface;
    color: $text;
    overflow: hidden;
}

/* ==========================================================================
   LOGIN SCREEN
   ========================================================================== */

.login-screen {
    align: center middle;
    height: 100%;
    width: 100%;
}

.login-container {
    width: 70;
    max-width: 80;
    padding: 2 4;
    background: $panel;
    border: thick $primary;
    align: center middle;
}

.login-title {
    color: $accent;
    text-style: bold;
    text-align: center;
    margin-bottom: 1;
    width: 100%;
}

.login-subtitle {
    color: $text-muted;
    text-align: center;
    margin-bottom: 2;
}

.login-section {
    color: $accent;
    text-style: bold;
    margin: 1 0;
    text-align: center;
}

.login-instruction {
    color: $text;
    margin: 1 0;
    text-align: center;
}

.login-error {
    color: $error;
    text-style: bold;
    margin: 1 0;
    text-align: center;
}

.login-input {
    width: 100%;
    margin: 1 0;
}

.login-button {
    width: 100%;
    margin: 1 0;
}

/* ==========================================================================
   HEADER & FOOTER
   ========================================================================== */

Header {
    background: $primary;
    color: $text-on-primary;
    text-style: bold;
    padding: 0 1;
}

Header .header--title {
    color: $text-on-primary;
}

Footer {
    background: $panel;
    color: $text;
}

Footer .footer--key {
    background: $primary;
    color: $text-on-primary;
}

Footer .footer--description {
    color: $text-muted;
}

/* ==========================================================================
   DASHBOARD SCREEN
   ========================================================================== */

.dashboard-screen {
    height: 100%;
}

.dashboard-container {
    padding: 1 2;
    height: 100%;
    layout: vertical;
}

/* Stats Bar */
.stats-bar {
    height: auto;
    min-height: 5;
    background: $panel;
    margin: 1 0;
    padding: 1;
    layout: horizontal;
}

.stat-box {
    width: 1fr;
    padding: 1;
    align: center middle;
}

.stat-value {
    text-style: bold;
    color: $accent;
    text-align: center;
    text-opacity: 1;
}

.stat-label {
    color: $text;
    text-align: center;
    text-opacity: 1;
}

/* Main Content */
.main-content {
    height: 1fr;
    layout: horizontal;
}

.left-panel {
    width: 1fr;
    height: 100%;
}

.right-panel {
    width: 1fr;
    height: 100%;
}

/* ==========================================================================
   CARDS
   ========================================================================== */

.card {
    background: $panel;
    border: round $primary;
    margin: 1;
    padding: 1 2;
    height: auto;
}

.card-header {
    text-style: bold;
    color: $accent;
    margin-bottom: 1;
    text-opacity: 1;
}

.card-title {
    text-style: bold;
    color: $text;
    margin-bottom: 1;
    text-opacity: 1;
}

.card-content {
    color: $text;
    margin: 1 0;
    text-opacity: 1;
}

.card-value {
    color: $text;
    text-opacity: 1;
}

/* ==========================================================================
   MODEL CARDS
   ========================================================================== */

.model-card {
    height: auto;
    min-height: 5;
    background: $surface;
    border: round $border;
    margin: 1 0;
    padding: 1;
}

.model-card.running {
    border: round $success;
}

.model-card.available {
    border: round $accent;
}

.model-card.stopped {
    border: round $error;
}

.model-card.loading {
    border: round $warning;
}

.model-header {
    height: auto;
    layout: horizontal;
    margin-bottom: 1;
}

.model-name {
    text-style: bold;
    color: $text;
    width: 1fr;
    text-opacity: 1;
}

.model-info {
    height: auto;
    color: $text-muted;
    text-opacity: 1;
}

.model-caps {
    height: auto;
    color: $accent;
    text-opacity: 1;
}

/* ==========================================================================
   AGENT CARDS
   ========================================================================== */

.agent-card {
    height: auto;
    min-height: 6;
    background: $surface;
    border: round $border;
    margin: 1 0;
    padding: 1;
}

.agent-card.running {
    border: round $success;
}

.agent-card.idle {
    border: round $warning;
}

.agent-card.paused {
    border: round $accent;
}

.agent-card.error {
    border: round $error;
}

.agent-header {
    height: auto;
    layout: horizontal;
    margin-bottom: 1;
}

.agent-name {
    text-style: bold;
    color: $text;
    width: 1fr;
    text-opacity: 1;
}

.agent-info {
    color: $text-muted;
    text-opacity: 1;
}

.agent-stats {
    color: $text;
    text-opacity: 1;
}

/* ==========================================================================
   STATUS INDICATORS
   ========================================================================== */

.status-indicator {
    text-align: right;
    color: $text;
}

.status-online {
    color: $success;
    text-opacity: 1;
}

.status-offline {
    color: $error;
    text-opacity: 1;
}

.status-limited {
    color: $warning;
    text-opacity: 1;
}

.status-running {
    color: $accent;
    text-opacity: 1;
}

.status-idle {
    color: $text-muted;
    text-opacity: 1;
}

.status-available {
    color: $success;
    text-opacity: 1;
}

.status-loading {
    color: $warning;
    text-opacity: 1;
}

.status-error {
    color: $error;
    text-opacity: 1;
}

/* ==========================================================================
   TASK ITEMS
   ========================================================================== */

.task-item {
    height: auto;
    min-height: 2;
    padding: 1;
    margin: 0 1;
}

.task-item.pending {
    color: $warning;
    text-opacity: 1;
}

.task-item.running {
    color: $accent;
    text-style: bold;
    text-opacity: 1;
}

.task-item.completed {
    color: $success;
    text-opacity: 1;
}

.task-item.failed {
    color: $error;
    text-opacity: 1;
}

.task-item.cancelled {
    color: $text-muted;
    text-opacity: 1;
}

.task-header {
    layout: horizontal;
}

.task-title {
    text-style: bold;
    color: $text;
    width: 1fr;
    text-opacity: 1;
}

.task-status {
    color: $text-muted;
    text-opacity: 1;
}

/* ==========================================================================
   SIDEBAR
   ========================================================================== */

.sidebar {
    width: 20;
    dock: left;
    background: $panel;
}

.sidebar-item {
    height: 3;
    padding: 0 1;
    align: left middle;
    color: $text;
}

.sidebar-item:hover {
    background: $surface;
}

.sidebar-item.active {
    background: $primary;
    color: $text-on-primary;
}

.sidebar-item:focus {
    background: $primary;
    color: $text-on-primary;
    text-style: bold;
}

/* ==========================================================================
   CHAT INTERFACE
   ========================================================================== */

.chat-screen {
    height: 100%;
}

.chat-container {
    height: 100%;
    layout: vertical;
}

.chat-header {
    background: $panel;
    padding: 1 2;
    margin-bottom: 1;
}

.chat-title {
    text-style: bold;
    color: $accent;
    text-opacity: 1;
}

.chat-model-info {
    color: $text-muted;
    text-opacity: 1;
}

.chat-messages {
    height: 1fr;
    background: $surface;
    border: round $border;
    padding: 1;
    overflow-y: scroll;
}

.chat-input-area {
    dock: bottom;
    height: auto;
    min-height: 3;
    background: $panel;
    padding: 1;
}

.message-user {
    color: $accent;
    margin: 1 0;
    text-opacity: 1;
}

.message-assistant {
    color: $text;
    margin: 1 0;
    text-opacity: 1;
}

.message-system {
    color: $text-muted;
    margin: 1 0;
    text-opacity: 1;
}

.message-error {
    color: $error;
    margin: 1 0;
    text-opacity: 1;
}

/* ==========================================================================
   BUTTONS
   ========================================================================== */

Button {
    margin: 0 1;
    min-width: 10;
    background: $surface;
    color: $text;
    border: round $border;
}

Button:hover {
    background: $primary;
    color: $text-on-primary;
    border: round $primary;
}

Button:focus {
    text-style: bold;
    background: $primary;
    color: $text-on-primary;
    border: round $primary;
}

Button.-primary {
    background: $primary;
    color: $text-on-primary;
    border: round $primary;
}

Button.-primary:hover {
    background: $primary-lighten;
}

Button.-error {
    background: $error;
    color: $text-on-primary;
    border: round $error;
}

Button.-success {
    background: $success;
    color: $text-on-primary;
    border: round $success;
}

Button.-warning {
    background: $warning;
    color: $text;
    border: round $warning;
}

/* ==========================================================================
   INPUTS
   ========================================================================== */

Input {
    margin: 1 0;
    background: $surface;
    border: round $border;
    color: $text;
    padding: 0 1;
}

Input:focus {
    border: round $accent;
}

Input .input--placeholder {
    color: $text-muted;
}

Input.-valid {
    border: round $success;
}

Input.-invalid {
    border: round $error;
}

/* ==========================================================================
   TABS
   ========================================================================== */

TabbedContent {
    height: 1fr;
}

Tabs {
    background: $panel;
}

Tab {
    background: $surface;
    color: $text;
    padding: 1 2;
}

Tab:hover {
    background: $primary;
    color: $text-on-primary;
}

Tab.-active {
    background: $primary;
    color: $text-on-primary;
    text-style: bold;
}

TabPane {
    padding: 1;
    background: $surface;
}

/* ==========================================================================
   PANELS
   ========================================================================== */

.panel {
    background: $panel;
    padding: 1;
    margin: 1;
}

.panel-horizontal {
    height: auto;
    background: $panel;
    padding: 1;
    margin: 1;
    layout: horizontal;
}

/* ==========================================================================
   SCROLL CONTAINERS
   ========================================================================== */

.scroll-container {
    height: 1fr;
    overflow-y: scroll;
    background: $surface;
}

VerticalScroll {
    background: transparent;
}

HorizontalScroll {
    background: transparent;
}

/* ==========================================================================
   SYSTEM STATUS
   ========================================================================== */

.system-status {
    background: $panel;
    border: round $border;
    padding: 1 2;
    margin: 1 0;
}

.status-bar {
    height: auto;
    layout: horizontal;
}

.status-item {
    color: $text;
    margin: 0 2;
    text-opacity: 1;
}

.progress-bar {
    height: 1;
    background: $surface;
    color: $accent;
}

/* ==========================================================================
   HELP TEXT
   ========================================================================== */

.help-text {
    color: $text-muted;
    text-align: center;
    margin: 1;
}

.help-key {
    background: $primary;
    color: $text-on-primary;
    padding: 0 1;
}

/* ==========================================================================
   EMPTY STATE
   ========================================================================== */

.empty-state {
    color: $text-muted;
    text-align: center;
    padding: 2;
    text-opacity: 1;
}

.empty-icon {
    color: $text-muted;
    text-align: center;
}

/* ==========================================================================
   LISTS
   ========================================================================== */

ListView {
    background: $surface;
}

ListItem {
    background: $surface;
    color: $text;
    padding: 1;
}

ListItem:hover {
    background: $panel;
}

ListItem.-active {
    background: $primary;
    color: $text-on-primary;
}

/* ==========================================================================
   MODALS & DIALOGS
   ========================================================================== */

.modal {
    align: center middle;
}

.modal-content {
    background: $panel;
    border: thick $primary;
    padding: 1 2;
    max-width: 60;
}

.modal-header {
    text-style: bold;
    color: $accent;
    margin-bottom: 1;
}

.modal-body {
    color: $text;
    margin: 1 0;
}

.modal-footer {
    layout: horizontal;
    margin-top: 1;
}

/* ==========================================================================
   NOTIFICATIONS
   ========================================================================== */

.notification {
    background: $panel;
    border: round $primary;
    padding: 1;
    margin: 1;
}

.notification-error {
    background: $error;
    color: $text-on-primary;
    border: round $error;
}

.notification-success {
    background: $success;
    color: $text-on-primary;
    border: round $success;
}

.notification-warning {
    background: $warning;
    color: $text;
    border: round $warning;
}

/* ==========================================================================
   SETTINGS SCREEN
   ========================================================================== */

.settings-container {
    height: 100%;
    padding: 1 2;
}

.settings-section {
    background: $panel;
    border: round $border;
    padding: 1 2;
    margin: 1 0;
}

.settings-label {
    color: $text;
    text-style: bold;
    margin: 1 0;
}

.settings-value {
    color: $text-muted;
}

/* ==========================================================================
   TASKS SCREEN
   ========================================================================== */

.tasks-container {
    height: 100%;
    padding: 1 2;
}

.tasks-toolbar {
    layout: horizontal;
    background: $panel;
    padding: 1;
    margin: 1 0;
}

.tasks-list {
    height: 1fr;
    overflow-y: scroll;
}

/* ==========================================================================
   MODELS SCREEN
   ========================================================================== */

.models-container {
    height: 100%;
    padding: 1 2;
}

.provider-section {
    background: $panel;
    border: round $border;
    padding: 1 2;
    margin: 1 0;
}

.provider-header {
    text-style: bold;
    color: $accent;
    margin-bottom: 1;
}

.provider-status {
    color: $text-muted;
}

/* ==========================================================================
   AGENTS SCREEN
   ========================================================================== */

.agents-container {
    height: 100%;
    padding: 1 2;
}

.agents-grid {
    layout: horizontal;
    height: 1fr;
}
"""


# Theme definitions
THEMES: dict[str, dict[str, str]] = {
    "default": {
        "primary": "#7c3aed",
        "primary-lighten": "#8b5cf6",
        "accent": "#06b6d4",
        "success": "#10b981",
        "warning": "#f59e0b",
        "error": "#ef4444",
        "surface": "#1e1e2e",
        "panel": "#2a2a3e",
        "background": "#0f0f1a",
        "text": "#e4e4e7",
        "text-muted": "#71717a",
        "text-on-primary": "#ffffff",
        "border": "#4a4a5a",
    },
    "dark": {
        "primary": "#6366f1",
        "primary-lighten": "#818cf8",
        "accent": "#22d3ee",
        "success": "#34d399",
        "warning": "#fbbf24",
        "error": "#f87171",
        "surface": "#18181b",
        "panel": "#27272a",
        "background": "#09090b",
        "text": "#fafafa",
        "text-muted": "#71717a",
        "text-on-primary": "#ffffff",
        "border": "#3f3f46",
    },
    "light": {
        "primary": "#6366f1",
        "primary-lighten": "#4f46e5",
        "accent": "#0891b2",
        "success": "#059669",
        "warning": "#d97706",
        "error": "#dc2626",
        "surface": "#ffffff",
        "panel": "#f4f4f5",
        "background": "#fafafa",
        "text": "#18181b",
        "text-muted": "#71717a",
        "text-on-primary": "#ffffff",
        "border": "#d4d4d8",
    },
    "dracula": {
        "primary": "#bd93f9",
        "primary-lighten": "#caa9fa",
        "accent": "#8be9fd",
        "success": "#50fa7b",
        "warning": "#ffb86c",
        "error": "#ff5555",
        "surface": "#282a36",
        "panel": "#44475a",
        "background": "#1e1f29",
        "text": "#f8f8f2",
        "text-muted": "#6272a4",
        "text-on-primary": "#282a36",
        "border": "#44475a",
    },
    "nord": {
        "primary": "#81a1c1",
        "primary-lighten": "#88c0d0",
        "accent": "#8fbcbb",
        "success": "#a3be8c",
        "warning": "#ebcb8b",
        "error": "#bf616a",
        "surface": "#2e3440",
        "panel": "#3b4252",
        "background": "#242933",
        "text": "#eceff4",
        "text-muted": "#d8dee9",
        "text-on-primary": "#2e3440",
        "border": "#4c566a",
    },
}


def get_theme_css(theme_name: ThemeName = "default") -> str:
    """Get CSS with theme variables substituted.
    
    Args:
        theme_name: Name of the theme to use.
        
    Returns:
        CSS string with theme variables.
    """
    theme = THEMES.get(theme_name, THEMES["default"])
    
    css = CSS
    
    # Replace theme variables
    for var_name, var_value in theme.items():
        css = css.replace(f"${var_name}", var_value)
        css = css.replace(f"${var_name.replace('_', '-')}", var_value)
    
    return css


def get_available_themes() -> list[str]:
    """Get list of available theme names.
    
    Returns:
        List of theme names.
    """
    return list(THEMES.keys())


def get_theme_colors(theme_name: ThemeName = "default") -> dict[str, str]:
    """Get color palette for a theme.
    
    Args:
        theme_name: Name of the theme.
        
    Returns:
        Dictionary of color variables.
    """
    return THEMES.get(theme_name, THEMES["default"]).copy()
