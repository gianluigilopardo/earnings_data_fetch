import io
import os
import json
from datetime import datetime
import time
from tqdm import tqdm


class ProgressTracker:
    """
    Tracks the progress and statistics of a process and saves progress info to a file.
    """

    def __init__(self, info_path, default_info, retrieve_prev=True):
        self.info_path = info_path
        self.info = default_info
        self.info['process_starts_at'] = self.current_datetime()
        self.start_time = time.time()  # Record start time

        # Load previous progress if available and requested
        if retrieve_prev and os.path.exists(info_path):
            with open(info_path, 'r') as f:
                existing_info = json.load(f)
                self._merge_existing_info(existing_info)

    def _merge_existing_info(self, existing_info):
        """Merges existing info with the current session's default info."""
        self.info['start_year'] = min(existing_info.get('start_year', self.info['start_year']),
                                      self.info['start_year'])
        self.info['end_year'] = max(existing_info.get('end_year', self.info['end_year']),
                                    self.info['end_year'])
        self.info['process_time'] += existing_info.get('process_time', 0.0)

    def save_info(self):
        """Saves the progress info to a JSON file."""
        self.info['process_ends_at'] = self.current_datetime()
        self.info['process_time'] = round(time.time() - self.start_time, 2)
        with open(self.info_path, 'w') as f:
            json.dump(self.info, f, indent=2)

    def finalize_info(self):
        """Finalizes progress info by setting the count of unique processed stocks."""
        self.info['processed_stocks'] = len(self.info.get('stocks', {}))

    def update_info(self, updates):
        """Updates the progress information."""
        self.info.update(updates)

    @staticmethod
    def current_datetime():
        """Returns the current date and time as a formatted string."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get(self, key, default=None):
        """Retrieves a value from the progress info."""
        return self.info.get(key, default)


def initialize_info(info_path, start_year, end_year, expected_to_process, key_name=None, retrieve_prev=True,
                    **additional_info):
    """
    Initializes the ProgressTracker with default information and additional attributes if provided.
    """
    default_info = {
        'process_starts_at': ProgressTracker.current_datetime(),
        'process_ends_at': ProgressTracker.current_datetime(),
        'process_time': 0.0,
        'expected_to_process': expected_to_process,
        f'processed_{key_name}': 0,
        'processed_stocks': 0,
        'unprocessed_stocks': [],
        'start_year': start_year,
        'end_year': end_year,
        'stocks': {},
    }
    if additional_info:
        default_info.update(additional_info)
    return ProgressTracker(info_path, default_info, retrieve_prev)


def update_progress_info(progress_tracker, stock, n_items, key_name):
    """
    Updates the progress information for a given stock.
    """
    if 'stocks' not in progress_tracker.info:
        progress_tracker.info['stocks'] = {}

    stock_info = progress_tracker.info['stocks'].setdefault(stock, {})

    # Update item count for the stock and overall count for the key
    stock_info[f'n_{key_name}'] = stock_info.get(f'n_{key_name}', 0) + n_items
    progress_tracker.info[f'processed_{key_name}'] += n_items

    if n_items == 0:
        progress_tracker.info['unprocessed_stocks'].append(stock)


def save_csv(dataframe, dir_path, filename, separator=',', encoding='utf-8-sig', sort_by_cols=None):
    """
    Saves a Polars DataFrame as a CSV file with optional sorting.
    """
    setup_directory(dir_path)
    file_path = os.path.join(dir_path, filename)
    buffer = io.StringIO()

    if sort_by_cols:
        dataframe = dataframe.sort(sort_by_cols)
    dataframe.write_csv(buffer, separator=separator)

    with open(file_path, 'w', encoding=encoding) as f:
        f.write(buffer.getvalue())


def setup_directory(directory_path):
    """
    Creates a directory if it doesn't already exist.
    """
    os.makedirs(directory_path, exist_ok=True)


def process_items(items, task_function, expected_to_process, *args, desc='Processing items'):
    """
    Processes a list of items with a given task function and tracks progress.
    """
    results = []
    with tqdm(total=expected_to_process, desc=desc) as pbar:
        for item in items:
            result = task_function(item, *args)
            results.append(result)
            pbar.update(result if isinstance(result, int) else len(result))
    return results
