#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Date: 04/010/2024
    Author: Joshua David Golafshan
"""

import streamlit as st


def user_component(session_id):
    st.markdown(f"""
        <div class="floating-user-id" onmouseenter="revealSessionID()">
            <span>🆔</span>
            <span class="session-id">{session_id}</span>
            <span class="reveal-hint">Hover to reveal</span>
        </div>
    """, unsafe_allow_html=True)


def title_divider():
    st.markdown(
        "<hr style='margin-top:-0.5rem;margin-bottom:2rem;'>",
        unsafe_allow_html=True
    )


def option_metric(css_style: str, option_type: str, option_price: float, option_delta: float, option_theta: float,
                  option_rho: float, option_gamma: float, option_vega: float):
    return f"""
        <div class="metric-container">
            <div class="{css_style}">
                <div class="metric-item">
                    <div class="metric-label">{option_type}</div>
                    <div class="metric-value">${option_price:.2f}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Delta</div>
                    <div class="metric-value">{option_delta:.2f}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Theta</div>
                    <div class="metric-value">{option_theta:.2f}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Rho</div>
                    <div class="metric-value">{option_rho:.2f}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Gamma</div>
                    <div class="metric-value">{option_gamma:.2f}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Vega</div>
                    <div class="metric-value">{option_vega:.2f}</div>
                </div>
            </div>
        </div>
    """
