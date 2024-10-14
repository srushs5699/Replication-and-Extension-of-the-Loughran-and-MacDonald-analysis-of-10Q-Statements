import os
import re
import pandas as pd
import wrds
from datetime import timedelta


# Step 1: Load the cik_lookup.txt file with CIK-to-Ticker mapping
def load_cik_to_ticker_mapping(cik_lookup_file):
    """
    Load the CIK-to-Ticker mapping from the cik_lookup.txt file, which is tab-delimited.
    """
    # Read the file using tab ('\t') as the delimiter
    cik_lookup = pd.read_csv(cik_lookup_file, delimiter='\t', names=['ticker', 'cik'], dtype=str)

    # Set 'cik' as the index so we can easily look up tickers by CIK
    return cik_lookup.set_index('cik')


# Step 2: Extract CIK and Filing Dates from Filenames in the 'downloads' folder
def extract_filing_info_from_filenames(directory):
    """
    Extract CIK and filing dates from filenames in the specified directory.
    Assumes filenames are in the format: CIK_YYYY-MM-DD_10-Q.txt
    """
    filing_data = []

    # Regex pattern to extract the CIK and filing date from the filename
    pattern = re.compile(r"(\d{6,7})_(\d{4}-\d{2}-\d{2})_10-Q")

    # Loop through all files in the directory
    for filename in os.listdir(directory):
        if "10-Q" in filename and filename.endswith(".txt"):  # Only process 10-Q .txt files
            match = pattern.search(filename)
            if match:
                cik = match.group(1)
                filing_date = match.group(2)
                filing_data.append({
                    'cik': cik,
                    'filing_date': pd.to_datetime(filing_date)
                })

    return pd.DataFrame(filing_data)


# Step 3: Connect to WRDS
def connect_to_wrds():
    """ Establish a connection to the WRDS database. """
    try:
        db = wrds.Connection(wrds_username='ss17454')  # Replace with your WRDS username
        print("Connected to WRDS")
        return db
    except Exception as e:
        print("Failed to connect to WRDS:", e)
        return None


# Step 4: Fetch permno using Ticker from CRSP
def lookup_permno_from_ticker(db, ticker):
    """
    Function to look up the permno for a company based on its ticker.
    This queries WRDS for permno using the ticker symbol,
    and excludes tickers that contain a hyphen ('-').
    """


    ticker = ticker.upper()

    # Exclude tickers that contain a hyphen


    query = f"""
    SELECT permno
    FROM crsp.stocknames
    WHERE ticker = '{ticker}'
    """
    result = db.raw_sql(query)

    if not result.empty:
        return result['permno'].iloc[0]  # Return the first permno found
    else:
        print(f"Permno not found for ticker {ticker}")
        return None


# Step 5: Compute Cumulative Excess Returns
def compute_excess_returns(db, permno, filing_date, window=4):
    """
    Compute cumulative excess returns for a given permno and filing date.
    The window is set to 4 days, covering a 3-4 day trading period after the filing.
    """
    start_date = filing_date
    end_date = filing_date + timedelta(days=window)

    query = f"""
    SELECT a.date, a.ret, b.sprtrn, (a.ret - b.sprtrn) AS excess_return
    FROM crsp.dsf AS a
    JOIN crsp.dsp500 AS b ON a.date = b.caldt
    WHERE a.permno = {permno} AND a.date BETWEEN '{start_date}' AND '{end_date}'
    """
    data = db.raw_sql(query)

    if data.empty:
        return None

    # Sum the excess returns for the 3-4 day period
    cumulative_excess_return = data['excess_return'].sum()
    return cumulative_excess_return


# Main function to calculate cumulative excess returns based on the 10-Q filing dates from the filenames
def main():
    # Step 1: Load the cik_lookup.txt file
    cik_lookup_file = "cik_lookup.txt"  # Replace with the actual path to your cik_lookup.txt file
    cik_to_ticker_mapping = load_cik_to_ticker_mapping(cik_lookup_file)
    cik_to_ticker_mapping.to_csv('cik_ticker_file.csv')

    # Specify the relative path to the 'downloads' folder
    directory = "./downloads"

    # Step 2: Extract filing info (CIK and filing dates) from filenames
    filing_data = extract_filing_info_from_filenames(directory)
    filing_data.to_csv('filing_data.csv')

    # Step 3: Connect to WRDS
    db = connect_to_wrds()

    if db:
        results = []

        # Step 4: Loop through the extracted CIKs and filing dates
        for _, row in filing_data.iterrows():
            cik = row['cik']
            filing_date = row['filing_date']

            # Step 5: Find the ticker using the CIK from cik_lookup.txt
            if cik in cik_to_ticker_mapping.index:
                ticker = cik_to_ticker_mapping.loc[cik, 'ticker']
                print("Original ticker:", ticker)

                # Step 6: Handle tickers with hyphens
                ticker = ticker.replace("-", "")
                print("Cleaned ticker:", ticker)

                if isinstance(ticker, pd.Series):
                    # Take the first value from the Series
                    ticker = ticker.iloc[0]
                    print(f"Using first value from Series: {ticker}")

                # Step 7: Get the permno for this company using the ticker
                permno = lookup_permno_from_ticker(db, ticker)

                if permno:
                    # Step 8: Compute cumulative excess returns over the 3-4 day window after the filing date
                    excess_return = compute_excess_returns(db, permno, filing_date)

                    if excess_return is not None:
                        results.append({
                            'cik': cik,
                            'ticker': ticker,
                            'filing_date': filing_date,
                            'cumulative_excess_return': excess_return
                        })

        # Step 9: Convert results to a DataFrame and print
        results_df = pd.DataFrame(results)
        print(results_df)

        # Step 10: Save results to CSV (optional)
        results_df.to_csv('cumulative_excess_returns.csv', index=False)

        # Step 11: Close the connection
        db.close()


if __name__ == "__main__":
    main()
