import polars as pl
import yfinance as yf
import warnings
import os
import time

from utils.process import initialize_info, update_progress_info, save_csv, setup_directory


def task_function(stock, start_year, end_year):
    """
    Fetches stock data for a specific period.
    """
    stock_data = get_stock_values(stock, start_year, end_year)
    return stock_data


def get_stock_values(stock: str, start_year: int, end_year: int) -> pl.DataFrame:
    """
    Retrieves historical stock data with quarterly intervals.
    """
    schema = ['Year', 'Quarter', 'Symbol', 'Open', 'High', 'Low', 'Close', 'Volume']
    stock_ticker = yf.Ticker(stock)
    hist = stock_ticker.history(start=f"{start_year}-01-01", end=f"{end_year}-12-31", interval="3mo").reset_index()

    if not hist.empty:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=UserWarning)
            period = hist['Date'].dt.to_period('Q').astype(str).str.split('Q').to_numpy()
            years, quarters = zip(*period)
            hist['Year'], hist['Quarter'] = years, quarters
        hist['Symbol'] = stock_ticker.ticker
        return pl.DataFrame(hist[schema])

    return pl.DataFrame([])


def process_stock_values(stocks, start_year, end_year, output_dir):
    """
    Processes stock values for multiple stocks over a range of years.
    """
    # Initialize progress tracking for stock values
    info_path = os.path.join(output_dir, 'quarterly_stock_values.json')
    stock_values_info = initialize_info(info_path, start_year, end_year, expected_to_process=len(stocks),
                                        key_name='stock_values', retrieve_prev=False)
    all_stock_values = []

    # Process each stock
    for stock in stocks:
        start_time = time.time()  # Start time for processing
        stock_values = task_function(stock, start_year, end_year)
        processing_time = round(time.time() - start_time, 2)  # Calculate processing time
        all_stock_values.append(stock_values)

        # Update the progress tracker
        update_progress_info(stock_values_info, stock, len(stock_values), 'stock_values')
        stock_values_info.update_info({'process_time': processing_time})

    # Combine and save all stock values to CSV
    if all_stock_values:
        final_stock_values = pl.concat(all_stock_values)
        save_csv(final_stock_values, output_dir, 'stock_values.csv', separator=',')

    # Finalize and save progress info
    stock_values_info.finalize_info()
    stock_values_info.save_info()

    # Print summary
    print_stock_values_summary(stock_values_info)


def print_stock_values_summary(stock_values_info):
    """
    Prints a summary of the stock value fetching process.
    """
    total_values = stock_values_info.get('processed_stock_values', 0)
    processed_stocks = stock_values_info.get('processed_stocks', 0)
    total_time = stock_values_info.get('process_time', 0.0)

    print(f"\nDownloaded {total_values} stock values for {processed_stocks} stocks.")
    print(f"The process took {total_time} seconds.")

    if stock_values_info.info.get('unprocessed_stocks'):
        print(f"Stocks with no stock values: {stock_values_info.info['unprocessed_stocks']}.")
