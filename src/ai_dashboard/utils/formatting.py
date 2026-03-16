"""Formatting utilities."""

from __future__ import annotations


def format_bytes(size: int | float, precision: int = 2) -> str:
    """Format bytes to human readable string.
    
    Args:
        size: Size in bytes.
        precision: Decimal precision.
        
    Returns:
        Formatted string (e.g., "1.5 GB").
    """
    if size < 0:
        raise ValueError("Size cannot be negative")
    
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size_float = float(size)
    
    for unit in units:
        if size_float < 1024:
            return f"{size_float:.{precision}f} {unit}"
        size_float /= 1024
    
    return f"{size_float:.{precision}f} PB"


def format_duration(seconds: int | float) -> str:
    """Format duration in seconds to human readable string.
    
    Args:
        seconds: Duration in seconds.
        
    Returns:
        Formatted string (e.g., "2h 30m 15s").
    """
    if seconds < 0:
        raise ValueError("Duration cannot be negative")
    
    seconds = int(seconds)
    
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes, secs = divmod(seconds, 60)
        if secs == 0:
            return f"{minutes}m"
        return f"{minutes}m {secs}s"
    elif seconds < 86400:
        hours, remainder = divmod(seconds, 3600)
        minutes, secs = divmod(remainder, 60)
        if minutes == 0:
            return f"{hours}h"
        return f"{hours}h {minutes}m"
    else:
        days, remainder = divmod(seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        if hours == 0:
            return f"{days}d"
        return f"{days}d {hours}h"


def format_number(num: int | float, precision: int = 1) -> str:
    """Format large numbers to human readable string.
    
    Args:
        num: Number to format.
        precision: Decimal precision.
        
    Returns:
        Formatted string (e.g., "1.5M", "2.3B").
    """
    if num < 0:
        return f"-{format_number(abs(num), precision)}"
    
    if num < 1000:
        return str(int(num))
    elif num < 1_000_000:
        return f"{num / 1000:.{precision}f}K"
    elif num < 1_000_000_000:
        return f"{num / 1_000_000:.{precision}f}M"
    elif num < 1_000_000_000_000:
        return f"{num / 1_000_000_000:.{precision}f}B"
    else:
        return f"{num / 1_000_000_000_000:.{precision}f}T"
