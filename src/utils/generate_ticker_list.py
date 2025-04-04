# -*- coding: utf-8 -*-

"""
    Date: 04/04/2024
    Author: Joshua David Golafshan
"""
import json

import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
from typing import Optional, Any, List, Tuple

exchange_list = [
    {"exchange_name": "American Stock Exchange", "exchange_code": "AMEX"},
    {"exchange_name": "Australian Securities Exchange", "exchange_code": "ASX"},
    {"exchange_name": "Chicago Futures Exchange", "exchange_code": "CFE"},
    {"exchange_name": "EUREX Futures Exchange", "exchange_code": "EUREX"},
    {"exchange_name": "Foreign Exchange", "exchange_code": "FOREX"},
    {"exchange_name": "Global Indices", "exchange_code": "INDEX"},
    {"exchange_name": "LIFFE Futures and Options", "exchange_code": "LIFFE"},
    {"exchange_name": "London Stock Exchange", "exchange_code": "LSE"},
    {"exchange_name": "Minneapolis Grain Exchange", "exchange_code": "MGEX"},
    {"exchange_name": "NASDAQ Stock Exchange", "exchange_code": "NASDAQ"},
    {"exchange_name": "New York Board of Trade", "exchange_code": "NYBOT"},
    {"exchange_name": "New York Stock Exchange", "exchange_code": "NYSE"},
    {"exchange_name": "OTC Bulletin Board", "exchange_code": "OTCBB"},
    {"exchange_name": "Singapore Stock Exchange", "exchange_code": "SGX"},
    {"exchange_name": "Toronto Stock Exchange", "exchange_code": "TSX"},
    {"exchange_name": "Toronto Venture Exchange", "exchange_code": "TSXV"},
    {"exchange_name": "Mutual Funds", "exchange_code": "USMF"},
    {"exchange_name": "Winnipeg Commodity Exchange", "exchange_code": "WCE"},
]

starting_letter = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
                   'U', 'V', 'W', 'X', 'Y', 'Z']


def parse_html(exchange_code: str, first_letter: str) -> Optional[Any]:
    url = f"https://www.eoddata.com/stocklist/{exchange_code}/{first_letter}.htm"

    # Send GET request
    response = requests.get(url)

    # Check if request was successful
    if response.status_code != 200:
        print(f"Failed to fetch data for {exchange_code} - {first_letter}. Status Code: {response.status_code}")
        return None  # Return None to indicate failure

    # Parse the HTML
    return BeautifulSoup(response.text, "html.parser")


def extract_tickers(parsed_html: Any) -> List[Tuple[str, str]]:
    tickers = []

    # Find the table containing stock data
    table = parsed_html.find("table", class_="quotes")

    if not table:
        print("No stock data table found.")
        return tickers  # Return empty list if table is missing

    # Iterate through each row, extracting the first two columns directly
    for row in table.find_all("tr")[1:]:  # Skip the header row
        cols = row.find_all("td")

        if len(cols) > 1:  # Ensure there are at least two columns
            ticker = cols[0].text.strip()  # First column: Ticker symbol
            company_name = cols[1].text.strip()  # Second column: Company name
            tickers.append((ticker, company_name))

    return tickers


def run(letters=None) -> List[Any]:
    """
    Fetches tickers from all exchanges for each letter.

    Args:
        letters (List[str], optional): Subset of letters to fetch. Defaults to A-Z.

    Returns:
        List[Tuple[str, str]]: List of (ticker, company_name).
    """
    if letters is None:
        letters = starting_letter  # Default to A-Z

    all_tickers = []  # Store all tickers and names

    for exchange in tqdm(exchange_list, desc="Fetching Exchanges"):
        exchange_code = exchange["exchange_code"]
        exchange_name = exchange["exchange_name"]

        for letter in tqdm(letters, desc=f"{exchange_code} - Letters", leave=False):
            try:
                html = parse_html(exchange_code, letter)

                if html:
                    tickers_and_names = extract_tickers(html)
                    for ticker, name in tickers_and_names:

                        all_tickers.append((ticker, name, exchange_code, exchange_name))

            except Exception as e:
                print(f"❌ Error fetching {exchange_code} - {letter}: {e}")

    # Summary
    print(f"\n✅ Total Tickers Fetched: {len(all_tickers)}")
    return all_tickers  # Return collected data


def save_to_json(data, filename="tickers.json"):
    """
    Saves the list of tickers and company names to a JSON file.

    Args:
        data (List[Tuple[str, str]]): List of (ticker, company_name) tuples.
        filename (str): Name of the JSON file to save.
    """
    try:
        # Convert list of tuples to a list of dictionaries
        json_data = [
            {"ticker": ticker, "company_name": name, "exchange_name": exchange_name, "exchange_code": exchange_code}
            for ticker, name, exchange_name, exchange_code in data
        ]

        # Save to JSON file
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=4, ensure_ascii=False)

        print(f"✅ Data successfully saved to {filename}")
    except Exception as e:
        print(f"❌ Error saving data to JSON: {e}")


# Example usage:
tickers = run()
save_to_json(tickers)
