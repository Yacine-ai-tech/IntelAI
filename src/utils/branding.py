"""
Logo and Branding Utilities for IntelAI

Handles logo display, branding elements, and visual identity across the platform.
"""
from __future__ import annotations

import base64
from pathlib import Path
from typing import Optional

from src.core.logger import get_logger

log = get_logger(__name__)

LOGO_PATH = Path(__file__).resolve().parent.parent.parent / "logo" / "IntelAI.png"


def get_logo_base64() -> Optional[str]:
    """Get the logo as base64 encoded string."""
    try:
        if LOGO_PATH.exists():
            with open(LOGO_PATH, "rb") as f:
                logo_data = f.read()
                return base64.b64encode(logo_data).decode()
        else:
            log.warning("Logo file not found at: %s", LOGO_PATH)
            return None
    except Exception as e:
        log.error("Failed to load logo: %s", e)
        return None


def get_header_html(include_logo: bool = True) -> str:
    """Get HTML header with logo for the application."""
    logo_b64 = get_logo_base64()
    
    if include_logo and logo_b64:
        logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="height: 60px; margin-right: 20px; vertical-align: middle;" />'
    else:
        logo_html = '<span style="font-size: 48px; margin-right: 20px;">🏢</span>'
    
    # Use the 2026 system brand consistently across the app
    html = f"""
    <div style="display: flex; align-items: center; padding: 20px 0; border-bottom: 2px solid #f0f0f0;">
        {logo_html}
        <div>
            <h1 style="margin: 0; color: #1f77b4;">IntelAI 2026</h1>
            <p style="margin: 0; color: #666; font-size: 14px;">Unified Multi-Domain Intelligence Platform</p>
        </div>
    </div>
    """
    return html


def get_sidebar_logo_html() -> str:
    """Get HTML for sidebar logo display."""
    logo_b64 = get_logo_base64()
    
    if logo_b64:
        html = f"""
        <div style="text-align: center; padding: 20px 0;">
            <img src="data:image/png;base64,{logo_b64}" style="width: 80%; max-width: 200px;" />
            <p style="margin-top: 10px; font-size: 12px; color: #666;">IntelAI 2026</p>
        </div>
        """
    else:
        html = """
        <div style="text-align: center; padding: 20px 0;">
            <div style="font-size: 48px;">🏢</div>
            <h3 style="margin: 10px 0;">IntelAI</h3>
            <p style="font-size: 12px; color: #666;">2026</p>
        </div>
        """
    return html


def get_export_logo_path() -> str:
    """Get the logo path for PDF/PPT exports."""
    return str(LOGO_PATH) if LOGO_PATH.exists() else ""


def get_branding_colors() -> dict:
    """Get the IntelAI branding color palette."""
    return {
        "primary": "#1f77b4",      # Blue
        "secondary": "#ff7f0e",    # Orange
        "success": "#2ca02c",      # Green
        "warning": "#ffbb00",      # Yellow
        "danger": "#d62728",       # Red
        "info": "#17becf",         # Cyan
        "dark": "#2c3e50",         # Dark Blue Gray
        "light": "#ecf0f1",        # Light Gray
        "finance": "#1f77b4",      # Blue for Finance
        "growth": "#2ca02c",       # Green for Growth
        "operations": "#ff7f0e",   # Orange for Operations
        "people": "#9467bd",       # Purple for People/HR
        "esg": "#8c564b",          # Brown for ESG
    }
