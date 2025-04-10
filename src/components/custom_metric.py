#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Date: 04/010/2024
    Author: Joshua David Golafshan
"""


def option_metric(css_style: str, option_type: str, option_price: float, option_delta: float, option_theta: float, option_rho: float):
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
            </div>
        </div>
    """
