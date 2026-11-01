"""
KPI Cards Component
Provides styled executive metric cards for Streamlit dashboards.
"""

import streamlit as st


def render_kpi_card(title: str, value: str, delta: str = None, is_positive: bool = True, subtitle: str = ""):
    """Renders a modern, styled card with metric values and trend pills."""
    delta_html = ""
    if delta:
        badge_bg = "#064E3B" if is_positive else "#7F1D1D"
        badge_color = "#34D399" if is_positive else "#F87171"
        icon = "▲" if is_positive else "▼"
        delta_html = f"""
        <span style="
            background-color: {badge_bg};
            color: {badge_color};
            padding: 3px 8px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-left: 8px;
            display: inline-block;">
            {icon} {delta}
        </span>
        """

    subtitle_html = (
        f"<div style='font-size: 0.75rem; color: #94A3B8; margin-top: 4px;'>{subtitle}</div>"
        if subtitle
        else ""
    )

    card_html = f"""
    <div style="
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        margin-bottom: 12px;">
        <div style="font-size: 0.825rem; font-weight: 500; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.05em;">
            {title}
        </div>
        <div style="display: flex; align-items: baseline; margin-top: 8px;">
            <span style="font-size: 1.75rem; font-weight: 700; color: #F8FAFC;">{value}</span>
            {delta_html}
        </div>
        {subtitle_html}
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
