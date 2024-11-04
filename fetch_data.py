from utils.args import parse_args
from utils.transcripts import process_transcripts
from utils.stock_values import process_stock_values

if __name__ == "__main__":
    # Parse command line arguments
    args = parse_args()
    stocks = args.stocks
    start_year = args.start_year
    end_year = args.end_year

    # Setup output directory
    data_dir = 'data'

    # Process transcripts and stock values
    process_transcripts(stocks, start_year, end_year, data_dir)
    process_stock_values(stocks, start_year, end_year, data_dir)
