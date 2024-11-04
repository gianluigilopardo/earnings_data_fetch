
# Earnings Data Fetch 

This repository contains Python scripts to fetch financial data, including earnings call transcripts and stock values. 

## Usage

1. **Clone the repository**:  
```bash 
git clone https://github.com/yourusername/earnings_data_fetch.git 
cd earnings_data_fetch
```

2. **Install dependencies**:
   Make sure to install the necessary Python packages listed in `requirements.txt`: 
```bash 
pip install -r requirements.txt
```

4. **Run data fetching**:
   Use the `fetch_data.py` script to start fetching the data:
```bash 
   python fetch_data.py
```
By default, this will fetch data for S&P500 firms from 2014 to 2024. 
Arguments can be adjusted to specify the stocks and years of interest. 

**Example**: if you want to fetch data for Apple and Microsoft stocks from 2020 to 2022, run: 
```bash 
   python fetch_data.py --stocks AAPL MSFT --start_year 2020 --end_year 2022
```

5. **Output**:
   - Data is saved in the `data/` directory: 
	   - quarterly stock values are saved in `data/quarterly_stock_values.py` 
	   - HTML files with earnings call transcripts are created for each selected company and stored in `data/{stock}/` 


## Notes

- Fetching transcripts involves sending requests to a public website, which may be subject to rate limits. 
- Progress tracking is implemented to allow for resuming interrupted processes. 

### Disclaimer 
The author assumes no responsibility for any consequences resulting from the use of this code. It is intended solely for personal, non-commercial use, and the user assumes all risk associated with its application and implementation. Any modification, distribution, or misuse of the code is done at the user's own discretion and responsibility. 
