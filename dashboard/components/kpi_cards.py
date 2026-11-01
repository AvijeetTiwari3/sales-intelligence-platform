"""
KPI Cards Component
Provides responsive, high-fidelity metric cards using Streamlit native metrics.
"""

import streamlit as st


def render_kpi_card(title: str, value: str, delta: str = None, is_positive: bool = True, subtitle: str = ""):
    """Renders a clean, responsive metric card."""
    with st.container():
        st.metric(
            label=title,
            value=value,
            delta=delta if delta else None,
            delta_color="normal" if is_positive else "inverse",
            help=subtitle if subtitle else None,
        )
