import os
import requests
from bs4 import BeautifulSoup
import time
from functools import partial
from utils.process import setup_directory, initialize_info, process_items, update_progress_info


def process_transcripts(stocks, start_year, end_year, output_dir):
    """
    Fetches transcripts for a list of stocks over a range of years and quarters.
    """
    expected_to_process = len(stocks) * (end_year - start_year + 1) * 4
    info_transcripts = os.path.join(output_dir, 'transcripts.json')
    progress_tracker = initialize_info(info_transcripts, start_year, end_year, expected_to_process,
                                       key_name='transcripts')

    # Partial function setup for stock transcript fetching
    partial_function = partial(fetch_transcript_for_stock, start_year=start_year, end_year=end_year,
                               output_dir=output_dir, progress_tracker=progress_tracker)

    # Process each stock's transcripts
    process_items(stocks, partial_function, expected_to_process, desc='Fetching transcripts')

    # Save and summarize progress
    progress_tracker.finalize_info()
    progress_tracker.save_info()
    print_transcript_summary(progress_tracker)


def fetch_transcript_for_stock(stock, start_year, end_year, output_dir, progress_tracker):
    """
    Fetches transcripts for a single stock for each quarter between start and end years.
    """
    stock_dir = os.path.join(output_dir, stock)
    setup_directory(stock_dir)

    fetched, missing = get_transcripts(stock, start_year, end_year, stock_dir)
    update_progress_info(progress_tracker, stock, fetched, 'transcripts')
    progress_tracker.info['stocks'][stock]['missing_transcripts'] = missing
    return fetched


def get_transcripts(stock, start_year, end_year, stock_dir):
    """
    Downloads earnings call transcripts for each quarter for a given stock.
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    total_fetched, missing_transcripts = 0, []

    with requests.Session() as session:
        session.headers.update(headers)
        for year in range(start_year, end_year + 1):
            for quarter in range(1, 5):
                file_path = os.path.join(stock_dir, f"{stock}_{year}_Q{quarter}.html")

                # Skip download if file already exists
                if os.path.exists(file_path):
                    total_fetched += 1
                    continue

                url = f"https://mlq.ai/stocks/{stock}/earnings-call-transcript/Q{quarter}-{year}"
                try:
                    response = session.get(url, timeout=5)
                    response.raise_for_status()

                    # Save transcript if content is valid, otherwise mark as missing
                    if save_transcript(response, file_path):
                        total_fetched += 1
                    else:
                        missing_transcripts.append(f"{year} Q{quarter}")

                except requests.exceptions.RequestException:
                    missing_transcripts.append(f"{year} Q{quarter}")

                # Pause to avoid rate limiting
                time.sleep(1)

    return total_fetched, missing_transcripts


def save_transcript(response, file_path):
    """
    Saves the transcript content from an HTTP response to a file,
    and returns True if successfully saved, False otherwise.
    """
    soup = BeautifulSoup(response.text, 'html.parser')
    transcript_div = soup.find('div', class_='transcript-content')

    # Only save if transcript content is available
    if transcript_div and "Transcript not available" not in transcript_div.text:
        with open(file_path, "w", encoding="utf-8-sig") as file:
            file.write(transcript_div.prettify())
        return True

    return False


def print_transcript_summary(progress_tracker):
    """
    Prints a summary of the transcript fetching process.
    """
    total = progress_tracker.get('processed_transcripts', 0)
    expected = progress_tracker.get('expected_to_process', 0)
    time_taken = progress_tracker.get('process_time', 0.0)
    print(f"\nFetched {total} transcripts out of {expected} in {time_taken} seconds.")
