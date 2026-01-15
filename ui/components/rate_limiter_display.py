"""
components/rate_limiter_display.py - Display rate limiter statistics

This component provides a visual display of current API rate limiting status
including RPM (Requests Per Minute) and TPM (Tokens Per Minute) usage.
"""

import streamlit as st
from typing import Dict, Optional


def render_rate_limiter_stats(stats: Optional[Dict] = None):
    """
    Render rate limiter statistics in a visual format.

    Args:
        stats: Dictionary with rate limiter statistics from RateLimiter.get_stats()
               If None, displays a placeholder/disabled state
    """
    if stats is None:
        # Display placeholder when no stats available
        st.markdown("""
        <div class="card">
            <div class="card-header">⚡ Rate Limiting Status</div>
            <div class="card-body">
                <p style="color: #888; text-align: center; padding: 20px;">
                    Rate limiting information will appear here during processing
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # Extract stats
    model = stats.get("model", "Unknown")
    current_rpm = stats.get("current_rpm", 0)
    rpm_limit = stats.get("rpm_limit", 0)
    rpm_percentage = stats.get("rpm_percentage", 0)
    current_tpm = stats.get("current_tpm", 0)
    tpm_limit = stats.get("tpm_limit", 0)
    tpm_percentage = stats.get("tpm_percentage", 0)

    # Determine status color based on usage
    def get_status_color(percentage):
        if percentage < 50:
            return "#27ca40"  # Green
        elif percentage < 80:
            return "#ffcc00"  # Yellow
        else:
            return "#ff6b6b"  # Red

    rpm_color = get_status_color(rpm_percentage)
    tpm_color = get_status_color(tpm_percentage)

    # Display rate limiter card
    st.markdown(f"""
    <div class="card fade-in">
        <div class="card-header">⚡ Rate Limiting Status - {model}</div>
        <div class="card-body">
            <div style="margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-weight: 600; color: #333;">Requests Per Minute (RPM)</span>
                    <span style="font-weight: 700; color: {rpm_color};">{current_rpm:,} / {rpm_limit:,}</span>
                </div>
                <div style="background: #f0f0f0; border-radius: 10px; height: 12px; overflow: hidden;">
                    <div style="
                        width: {min(rpm_percentage, 100)}%;
                        height: 100%;
                        background: linear-gradient(90deg, {rpm_color}, {rpm_color});
                        transition: width 0.5s ease;
                        border-radius: 10px;
                    "></div>
                </div>
                <div style="text-align: right; margin-top: 4px; font-size: 12px; color: #666;">
                    {rpm_percentage:.1f}% utilized
                </div>
            </div>

            <div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-weight: 600; color: #333;">Tokens Per Minute (TPM)</span>
                    <span style="font-weight: 700; color: {tpm_color};">{current_tpm:,} / {tpm_limit:,}</span>
                </div>
                <div style="background: #f0f0f0; border-radius: 10px; height: 12px; overflow: hidden;">
                    <div style="
                        width: {min(tpm_percentage, 100)}%;
                        height: 100%;
                        background: linear-gradient(90deg, {tpm_color}, {tpm_color});
                        transition: width 0.5s ease;
                        border-radius: 10px;
                    "></div>
                </div>
                <div style="text-align: right; margin-top: 4px; font-size: 12px; color: #666;">
                    {tpm_percentage:.1f}% utilized
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_rate_limiter_metrics(stats: Optional[Dict] = None):
    """
    Render rate limiter statistics as Streamlit metrics.

    Args:
        stats: Dictionary with rate limiter statistics from RateLimiter.get_stats()
    """
    if stats is None:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("RPM Usage", "N/A", help="Requests per minute")
        with col2:
            st.metric("TPM Usage", "N/A", help="Tokens per minute")
        return

    current_rpm = stats.get("current_rpm", 0)
    rpm_limit = stats.get("rpm_limit", 0)
    rpm_percentage = stats.get("rpm_percentage", 0)
    current_tpm = stats.get("current_tpm", 0)
    tpm_limit = stats.get("tpm_limit", 0)
    tpm_percentage = stats.get("tpm_percentage", 0)

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "RPM Usage",
            f"{current_rpm}/{rpm_limit}",
            delta=f"{rpm_percentage:.1f}%",
            help="Requests per minute usage"
        )

    with col2:
        st.metric(
            "TPM Usage",
            f"{current_tpm:,}/{tpm_limit:,}",
            delta=f"{tpm_percentage:.1f}%",
            help="Tokens per minute usage"
        )


def render_compact_rate_status(stats: Optional[Dict] = None):
    """
    Render a compact one-line rate limiter status.

    Args:
        stats: Dictionary with rate limiter statistics
    """
    if stats is None:
        st.info("⚡ Rate limiting: Inactive")
        return

    rpm_percentage = stats.get("rpm_percentage", 0)
    tpm_percentage = stats.get("tpm_percentage", 0)
    max_percentage = max(rpm_percentage, tpm_percentage)

    if max_percentage < 50:
        status = "🟢 Healthy"
        color = "#27ca40"
    elif max_percentage < 80:
        status = "🟡 Moderate"
        color = "#ffcc00"
    else:
        status = "🔴 High"
        color = "#ff6b6b"

    st.markdown(f"""
    <div style="
        padding: 12px 20px;
        border-radius: 8px;
        background: white;
        border-left: 4px solid {color};
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
    ">
        <strong>{status} Usage:</strong>
        RPM {rpm_percentage:.0f}% | TPM {tpm_percentage:.0f}%
    </div>
    """, unsafe_allow_html=True)
