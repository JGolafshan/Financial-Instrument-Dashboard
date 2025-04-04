#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Date: 03/04/2024
    Author: Joshua David Golafshan
"""

import json


def load_unique_objects(filename: str):
    # Open and load JSON data from file
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)

    unique_objects = []
    seen = set()

    for obj in data:
        # Convert dictionary to a hashable tuple (if obj is a dict)
        if isinstance(obj, dict):
            # Sorting ensures the tuple order is consistent for equivalent dicts
            obj_tuple = tuple(sorted(obj.items()))
        else:
            # If not a dict, we assume the object is already hashable
            obj_tuple = obj

        if obj_tuple not in seen:
            seen.add(obj_tuple)
            unique_objects.append(obj)

    return unique_objects


filename = 'data/tickers.json'  # Replace with your JSON file path
unique_data = load_unique_objects(filename)
print(f"Found {len(unique_data)} unique objects:")
