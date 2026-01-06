#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Date: 08/04/2024
    Author: Joshua David Golafshan
"""

static_page_names = ['pages/queries.py', 'pages/instruments.py', 'pages/search.py', 'pages/instrument.py', 'pages/home.py']
static_page_types = ['viewed', 'searched']

exchange_timezones = {
    "Universal": {
        "City": None,
        "Timezone": "UTC"
    },
    "US East": {
        "City": "New York",
        "Timezone": "America/New_York"
    },
    "UK": {
        "City": "London",
        "Timezone": "Europe/London"
    },
    "Germany": {
        "City": "Frankfurt",
        "Timezone": "Europe/Berlin"
    },
    "France": {
        "City": "Paris",
        "Timezone": "Europe/Paris"
    },
    "Switzerland": {
        "City": "Zurich",
        "Timezone": "Europe/Zurich"
    },
    "Japan": {
        "City": "Tokyo",
        "Timezone": "Asia/Tokyo"
    },
    "China": {
        "City": "Shanghai",
        "Timezone": "Asia/Shanghai"
    },
    "Hong Kong": {
        "City": "Hong Kong",
        "Timezone": "Asia/Hong_Kong"
    },
    "India": {
        "City": "Mumbai",
        "Timezone": "Asia/Kolkata"
    },
    "Australia": {
        "City": "Sydney",
        "Timezone": "Australia/Sydney"
    },
    "Brazil": {
        "City": "São Paulo",
        "Timezone": "America/Sao_Paulo"
    },
    "Canada": {
        "City": "Toronto",
        "Timezone": "America/Toronto"
    },
    "Middle East": {
        "City": "Dubai",
        "Timezone": "Asia/Dubai"
    },
    "Africa": {
        "City": "Johannesburg",
        "Timezone": "Africa/Johannesburg"
    }
}