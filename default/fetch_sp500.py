import requests
from bs4 import BeautifulSoup
from io import StringIO
import pandas as pd
import polars as pl

from utils.process import save_csv


def fetch_sp500_tickers():
    """
    Fetches the list of S&P 500 tickers from Wikipedia and saves the table to CSV.

    Returns:
        tuple: A Polars DataFrame of the S&P 500 companies and a list of stock symbols in lowercase.
    """
    try:
        # Wikipedia URL for the list of S&P 500 companies
        wiki_url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'

        # Get the webpage content
        response = requests.get(wiki_url)
        response.raise_for_status()  # Raise exception for HTTP errors

        # Parse HTML with BeautifulSoup and read tables into pandas DataFrames
        soup = BeautifulSoup(response.text, 'html.parser')
        tables = pd.read_html(StringIO(str(soup)))

        # Convert the first table to a Polars DataFrame and replace '.' in symbols with '-'
        sp500_table = pl.from_pandas(tables[0]).with_columns(
            pl.col('Symbol').str.replace('.', '-', literal=True).alias('Symbol')
        )

        # Save the table as a CSV file, sorted by 'Symbol'
        save_csv(sp500_table, 'data', 'sp500_table.csv', sort_by_cols=['Symbol'])

        # Extract the 'Symbol' column for a list of tickers
        tickers = sp500_table['Symbol'].to_list()

        return sp500_table, tickers

    except Exception as e:
        print(f"Error fetching S&P 500 tickers: {e}")
        return None, []
