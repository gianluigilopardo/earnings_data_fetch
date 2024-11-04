import datetime

from default.fetch_sp500 import fetch_sp500_tickers

# Fetch S&P 500 stock symbols
sp500_table, STOCKS = fetch_sp500_tickers()

# Set data fetching range
START_YEAR = 2014
END_YEAR = datetime.datetime.now().year
