#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Date: 03/04/2024
    Author: Joshua David Golafshan
"""
import datetime
import json
import random
import uuid
from src.utils.utils import insert_document

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


# filename = 'data/tickers.json'  # Replace with your JSON file path
# unique_data = load_unique_objects(filename)
# print(f"Found {len(unique_data)} unique objects:")


def generate_random_document():
    """
    Generates a random document with the following fields:
    - user_id: Random UUID
    - datetime: Random datetime within the last 30 days
    - page_url: Random URL from a predefined list
    - page_parameters: Random parameters (empty or with random keys/values)
    - use_type: Random use type (e.g., "viewed", "clicked", etc.)
    """
    # Generate a random user_id (UUID)
    user_id = str(uuid.uuid4())

    # Generate a random datetime within the last 30 days
    random_days = random.randint(0, 30)
    random_datetime = datetime.datetime.now() - datetime.timedelta(days=random_days)

    # Randomly select a page_url from a predefined list
    page_urls = ["/instrument", "/home", "/about", "/contact", "/services"]
    page_url = random.choice(page_urls)

    # Randomly generate page_parameters (empty or with random parameters)
    page_parameters = []
    if random.random() > 0.5:  # 50% chance of having parameters
        num_parameters = random.randint(1, 3)  # Random number of parameters (1 to 3)
        for _ in range(num_parameters):
            param_key = f"param{random.randint(1, 10)}"
            param_value = f"value{random.randint(1, 100)}"
            page_parameters.append({param_key: param_value})

    # Randomly select a use_type
    use_types = ["viewed", "clicked", "visited", "searched"]
    use_type = random.choice(use_types)

    # Create the random document
    document = {
        "user_id": user_id,
        "datetime_custom": random_datetime,
        "page_url": page_url,
        "page_parameters": page_parameters,
        "use_type": use_type
    }

    return document

