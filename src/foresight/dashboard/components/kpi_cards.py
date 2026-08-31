"""Ultra-modern 3D glassmorphic KPI cards with animated glow effects for Project FORESIGHT."""

import textwrap
import streamlit as st


def render_kpi_card(
    title: str,
    value: str,
    subtitle: str | None = None,
    delta: str | None = None,
    delta_color: str = "normal",
    border_color: str = "#00f0ff",
    theme: str = "cyan",  # cyan, purple, emerald, crimson, amber
    icon: str = "⚡",
) -> None:
    """Render a futuristic 3D glassmorphic KPI card with neon glowing borders and smooth hover animation."""
    
    theme_colors = {
        "cyan": {"border": "#00f0ff", "glow": "rgba(0, 240, 255, 0.25)", "text": "#38bdf8", "icon_bg": "rgba(0, 240, 255, 0.15)"},
        "purple": {"border": "#a855f7", "glow": "rgba(168, 85, 247, 0.25)", "text": "#c084fc", "icon_bg": "rgba(168, 85, 247, 0.15)"},
        "emerald": {"border": "#10b981", "glow": "rgba(16, 185, 129, 0.25)", "text": "#34d399", "icon_bg": "rgba(16, 185, 129, 0.15)"},
        "crimson": {"border": "#ff0055", "glow": "rgba(255, 0, 85, 0.25)", "text": "#fb7185", "icon_bg": "rgba(255, 0, 85, 0.15)"},
        "amber": {"border": "#f59e0b", "glow": "rgba(245, 158, 11, 0.25)", "text": "#fbbf24", "icon_bg": "rgba(245, 158, 11, 0.15)"},
    }
    
    cfg = theme_colors.get(theme, theme_colors["cyan"])
    if border_color != "#00f0ff":
        cfg["border"] = border_color
        
    delta_html = f'<div style="display:inline-flex;align-items:center;gap:4px;font-size:0.82rem;font-weight:600;color:#10b981;background:rgba(16,185,129,0.12);padding:3px 8px;border-radius:9999px;border:1px solid rgba(16,185,129,0.25);margin-top:6px;"><span>▲</span> {delta}</div>' if delta else ""
    sub_html = f'<div style="font-size:0.78rem;color:#94a3b8;margin-top:6px;font-weight:500;letter-spacing:0.02em;">{subtitle}</div>' if subtitle else ""

    html = textwrap.dedent(f"""
<div class="glow-card-3d" style="position:relative;background:linear-gradient(135deg, rgba(15,23,42,0.85) 0%, rgba(30,41,59,0.65) 100%);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);border:1px solid rgba(255,255,255,0.1);border-top:2px solid {cfg['border']};border-radius:14px;padding:18px 22px;margin-bottom:16px;box-shadow:0 10px 25px -5px rgba(0,0,0,0.5), 0 0 15px -3px {cfg['glow']};transition:all 0.35s cubic-bezier(0.4,0,0.2,1);overflow:hidden;transform:perspective(1000px) translateZ(0);">
<div style="position:absolute;top:-20px;right:-20px;width:80px;height:80px;background:{cfg['border']};filter:blur(40px);opacity:0.25;border-radius:50%;pointer-events:none;"></div>
<div style="display:flex;justify-content:space-between;align-items:flex-start;">
<div style="font-size:0.80rem;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:0.08em;">{title}</div>
<div style="display:flex;align-items:center;justify-content:center;width:32px;height:32px;border-radius:8px;background:{cfg['icon_bg']};border:1px solid {cfg['border']};font-size:1rem;box-shadow:0 0 10px {cfg['glow']};">{icon}</div>
</div>
<div style="font-size:2.1rem;font-weight:800;color:#ffffff;letter-spacing:-0.03em;margin-top:8px;text-shadow:0 2px 10px rgba(0,0,0,0.5), 0 0 20px {cfg['glow']};font-family:'Inter', -apple-system, sans-serif;">{value}</div>
<div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
{delta_html}
{sub_html}
</div>
</div>
""").strip()

    st.markdown(html, unsafe_allow_html=True)

