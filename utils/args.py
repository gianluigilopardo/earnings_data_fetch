import argparse

from default.params import *


def parse_args():
    """
    Parses command-line arguments for fetching financial data.

    Returns:
        argparse.Namespace: Parsed command-line arguments with stock symbols, start year, and end year.
    """
    parser = argparse.ArgumentParser(
        description='Fetch financial data.'
    )

    # Stock symbols to fetch
    parser.add_argument(
        '--stocks',
        type=str,
        default=STOCKS,
        nargs='*',
        help=f'List of stock symbols to fetch. Default: {STOCKS}.'
    )

    # Start year for data
    parser.add_argument(
        '--start_year',
        type=int,
        default=int(START_YEAR),
        help=f'Start year for data. Default: {START_YEAR}.'
    )

    # End year for data
    parser.add_argument(
        '--end_year',
        type=int,
        default=int(END_YEAR),
        help=f'End year for data. Default: {END_YEAR}.'
    )

    # Parse command-line arguments
    args = parser.parse_args()

    # Convert stocks to uppercase
    if args.stocks:
        args.stocks = [stock.upper() for stock in args.stocks]

    return args
