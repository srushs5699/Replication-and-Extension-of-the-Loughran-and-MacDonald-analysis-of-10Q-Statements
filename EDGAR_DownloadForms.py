

import requests
import pandas as pd
import os
from bs4 import BeautifulSoup
from time import sleep

# Function to download the CIK lookup file from SEC
def download_cik_lookup():
    url = 'https://www.sec.gov/include/ticker.txt'
    response = requests.get(url, headers={"User-Agent": "Your Name (your-email@example.com)"})
    
    if response.status_code == 200:
        with open('cik_lookup.txt', 'wb') as f:
            f.write(response.content)
        print("Downloaded CIK lookup file.")
    else:
        print(f"Failed to download CIK lookup file. Status code: {response.status_code}")

# Function to scrape S&P 500 tickers from Wikipedia
def get_sp500_tickers():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    response = requests.get(url)
    
    if response.status_code != 200:
        raise Exception(f"Failed to fetch S&P 500 tickers. Status code: {response.status_code}")

    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table', {'id': 'constituents'})  # The table on Wikipedia containing the tickers
    
    sp500_tickers = []
    for row in table.find_all('tr')[1:]:
        ticker = row.find_all('td')[0].text.strip()  # First column contains the ticker symbol
        sp500_tickers.append(ticker)
    
    return sp500_tickers

# Function to map S&P 500 tickers to CIKs and save to ticker.txt
def generate_ticker_file():
    # Step 1: Download the CIK lookup file from the SEC
    download_cik_lookup()
    
    # Step 2: Load CIK lookup into a dataframe
    cik_lookup_df = pd.read_csv('cik_lookup.txt', sep='\t', header=None, names=['ticker', 'cik'])
    
    # Convert tickers to uppercase as SEC CIK file uses uppercase tickers
    cik_lookup_df['ticker'] = cik_lookup_df['ticker'].str.upper()
    
    # Step 3: Fetch S&P 500 tickers from Wikipedia
    sp500_tickers = get_sp500_tickers()
    sp500_tickers = [ticker.upper() for ticker in sp500_tickers]  # Ensure uppercase

    # Step 4: Filter the CIK lookup file for only S&P 500 companies
    sp500_cik_df = cik_lookup_df[cik_lookup_df['ticker'].isin(sp500_tickers)]
    
    if sp500_cik_df.empty:
        print("No matching CIKs found for S&P 500 tickers.")
    else:
        # Step 5: Save the filtered data to ticker.txt
        sp500_cik_df.to_csv('ticker.txt', columns=['cik'], index=False)
        print(f"Saved {len(sp500_cik_df)} S&P 500 CIKs to ticker.txt.")

# Function to download a file from the SEC
def download_file(url, save_path):
    response = requests.get(url, headers={"User-Agent": "Your Name (your-email@example.com)"})
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded {save_path}")
    else:
        print(f"Failed to download {url}. Status code: {response.status_code}")

# Function to download forms for S&P 500 companies from the master index
def download_sp500_forms(master_index_file, sp500_ciks, start_year, end_year):
    df = pd.read_csv(master_index_file)
    
    # Create directory to store downloads if it doesn't exist
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    
    # Filter the dataframe for the relevant criteria
    filtered_df = df[(df['cik'].isin(sp500_ciks)) & 
                     (df['form'] == '10-Q') & 
                     (df['filing_date'].str[:4].astype(int).between(start_year, end_year))]
    
    print(f"Found {len(filtered_df)} 10-Q filings for S&P 500 companies between {start_year} and {end_year}.")
    
    # Download each filing
    for _, row in filtered_df.iterrows():
        cik = row['cik']
        filing_date = row['filing_date']
        file_path = row['path']
        company_name = row['name']
        
        # Construct the full URL for the filing
        url = f"https://www.sec.gov/Archives/{file_path}"
        save_path = f"downloads/{cik}_{filing_date}_10-Q.txt"
        
        # Download the file
        if not os.path.exists(save_path):
            # Download the file if it doesn't exist
            download_file(url, save_path)
            print(f"Downloaded: {save_path}")
            # Sleep between downloads to avoid overwhelming SEC servers
            sleep(1)  # 1 second delay between downloads
        else:
            print(f"File already exists: {save_path}, skipping download.")
        
        # Sleep between downloads to avoid overwhelming SEC servers
        sleep(1)  # 1 second delay between downloads

    return len(filtered_df)  # Return the number of downloaded filings

# Function to load S&P 500 CIKs from a ticker file (assumed CSV format)
def read_sp500_ciks(ticker_file):
    ticker_df = pd.read_csv(ticker_file)
    return set(ticker_df['cik'])

# Final check for total number of downloaded files
def check_downloaded_files():
    downloaded_files = os.listdir('downloads')
    print(f"Total files downloaded: {len(downloaded_files)}")
    return len(downloaded_files)

# Example usage
if __name__ == '__main__':
    # Step 1: Generate the ticker.txt file containing S&P 500 CIKs
    generate_ticker_file()  # This will download the CIKs for S&P 500 companies

    # Step 2: Read S&P 500 CIKs from the generated ticker.txt
    sp500_ciks = read_sp500_ciks('ticker.txt')

    # Step 3: Set the master index file (generated by EDGAR_Pac.py)
    master_index_file = 'master_index.csv'  # The consolidated master index from EDGAR_Pac

    # Step 4: Download 10-Q forms for the past 5 years (2018-2022)
    total_filings = download_sp500_forms(master_index_file, sp500_ciks, start_year=2019, end_year=2024)

    print(f"Expected to download approximately 10,000 filings. Downloaded: {total_filings}")

    # Step 5: Check the total number of downloaded files in the 'downloads' folder
    total_downloaded = check_downloaded_files()

    print(f"Final number of downloaded files: {total_downloaded}")

#CODE 2
# import requests
# import requests
# import pandas as pd
# import os
# import re  # For regular expressions to find MD&A section
# from bs4 import BeautifulSoup
# from time import sleep
# from fpdf import FPDF

# # Function to download the CIK lookup file from SEC
# def download_cik_lookup():
#     url = 'https://www.sec.gov/include/ticker.txt'
#     response = requests.get(url, headers={"User-Agent": "Your Name (your-email@example.com)"})
    
#     if response.status_code == 200:
#         with open('cik_lookup.txt', 'wb') as f:
#             f.write(response.content)
#         print("Downloaded CIK lookup file.")
#     else:
#         print(f"Failed to download CIK lookup file. Status code: {response.status_code}")

# # Function to scrape S&P 500 tickers from Wikipedia
# def get_sp500_tickers():
#     url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
#     response = requests.get(url)
    
#     if response.status_code != 200:
#         raise Exception(f"Failed to fetch S&P 500 tickers. Status code: {response.status_code}")

#     soup = BeautifulSoup(response.content, 'html.parser')
#     table = soup.find('table', {'id': 'constituents'})  # The table on Wikipedia containing the tickers
    
#     sp500_tickers = []
#     for row in table.find_all('tr')[1:]:
#         ticker = row.find_all('td')[0].text.strip()  # First column contains the ticker symbol
#         sp500_tickers.append(ticker)
    
#     return sp500_tickers

# # Function to map S&P 500 tickers to CIKs and save to ticker.txt
# def generate_ticker_file():
#     # Step 1: Download the CIK lookup file from the SEC
#     download_cik_lookup()
    
#     # Step 2: Load CIK lookup into a dataframe
#     cik_lookup_df = pd.read_csv('cik_lookup.txt', sep='\t', header=None, names=['ticker', 'cik'])
    
#     # Convert tickers to uppercase as SEC CIK file uses uppercase tickers
#     cik_lookup_df['ticker'] = cik_lookup_df['ticker'].str.upper()
    
#     # Step 3: Fetch S&P 500 tickers from Wikipedia
#     sp500_tickers = get_sp500_tickers()
#     sp500_tickers = [ticker.upper() for ticker in sp500_tickers]  # Ensure uppercase

#     # Step 4: Filter the CIK lookup file for only S&P 500 companies
#     sp500_cik_df = cik_lookup_df[cik_lookup_df['ticker'].isin(sp500_tickers)]
    
#     if sp500_cik_df.empty:
#         print("No matching CIKs found for S&P 500 tickers.")
#     else:
#         # Step 5: Save the filtered data to ticker.txt
#         sp500_cik_df.to_csv('ticker.txt', columns=['cik'], index=False)
#         print(f"Saved {len(sp500_cik_df)} S&P 500 CIKs to ticker.txt.")

# # Function to extract MD&A section from a 10-Q filing
# def extract_mda_section(text):
#     # Regular expression to find the start and end of MD&A section
#     mda_start = re.search(r"(?i)(Item\s+2[.:\s]+Management's Discussion and Analysis|MD&A)", text)
#     mda_end = re.search(r"(?i)(Item\s+3[.:\s]+Quantitative and Qualitative|Item 4)", text)

#     if mda_start and mda_end:
#         return text[mda_start.start():mda_end.start()]
#     elif mda_start:
#         # If the start is found but no clear end is found, extract from start to the end of the document
#         return text[mda_start.start():]
#     else:
#         return ""  # No MD&A section found

# # Function to save extracted MD&A section as PDF
# def save_mda_to_pdf(mda_text, pdf_path):
#     pdf = FPDF()
#     pdf.set_auto_page_break(auto=True, margin=15)
#     pdf.add_page()
#     pdf.set_font("Arial", size=12)

#     # Split the text into lines and add them to the PDF
#     for line in mda_text.split('\n'):
#         pdf.multi_cell(0, 10, line)

#     pdf.output(pdf_path)
#     print(f"MD&A saved as PDF: {pdf_path}")

# # Function to download and process a file from the SEC, saving as PDF
# def download_file_and_process_mdna(url, save_path):
#     response = requests.get(url, headers={"User-Agent": "Your Name (your-email@example.com)"})
    
#     if response.status_code == 200:
#         file_text = response.text

#         # Extract only the MD&A section
#         mda_section = extract_mda_section(file_text)

#         if mda_section:
#             # Save the MD&A section to a PDF
#             save_mda_to_pdf(mda_section, save_path)
#         else:
#             print(f"No MD&A section found in {url}")
#     else:
#         print(f"Failed to download {url}. Status code: {response.status_code}")

# # Function to download forms for S&P 500 companies from the master index
# def download_sp500_forms(master_index_file, sp500_ciks, start_year, end_year):
#     df = pd.read_csv(master_index_file)
    
#     # Create directory to store downloads if it doesn't exist
#     if not os.path.exists('downloads'):
#         os.makedirs('downloads')
    
#     # Filter the dataframe for the relevant criteria
#     filtered_df = df[(df['cik'].isin(sp500_ciks)) & 
#                      (df['form'] == '10-Q') & 
#                      (df['filing_date'].str[:4].astype(int).between(start_year, end_year))]
    
#     print(f"Found {len(filtered_df)} 10-Q filings for S&P 500 companies between {start_year} and {end_year}.")
    
#     # Download and process each filing
#     for _, row in filtered_df.iterrows():
#         cik = row['cik']
#         filing_date = row['filing_date']
#         file_path = row['path']
        
#         # Construct the full URL for the filing
#         url = f"https://www.sec.gov/Archives/{file_path}"
#         save_path = f"downloads/{cik}_{filing_date}_10-Q_MD&A.pdf"
        
#         # Check if the file already exists
#         if not os.path.exists(save_path):
#             # Download and process the file if it doesn't exist
#             download_file_and_process_mdna(url, save_path)
#             # Sleep between downloads to avoid overwhelming SEC servers
#             sleep(1)  # 1 second delay between downloads
#         else:
#             print(f"File already exists: {save_path}, skipping download.")

#     return len(filtered_df)  # Return the number of downloaded filings

# # Function to load S&P 500 CIKs from a ticker file (assumed CSV format)
# def read_sp500_ciks(ticker_file):
#     ticker_df = pd.read_csv(ticker_file)
#     return set(ticker_df['cik'])

# # Final check for total number of downloaded files
# def check_downloaded_files():
#     downloaded_files = os.listdir('downloads')
#     print(f"Total files downloaded: {len(downloaded_files)}")
#     return len(downloaded_files)

# # Example usage
# if __name__ == '__main__':
#     # Step 1: Generate the ticker.txt file containing S&P 500 CIKs
#     generate_ticker_file()  # This will download the CIKs for S&P 500 companies

#     # Step 2: Read S&P 500 CIKs from the generated ticker.txt
#     sp500_ciks = read_sp500_ciks('ticker.txt')

#     # Step 3: Set the master index file (generated by EDGAR_Pac.py)
#     master_index_file = 'master_index.csv'  # The consolidated master index from EDGAR_Pac

#     # Step 4: Download 10-Q forms for the past 5 years (2018-2022)
#     total_filings = download_sp500_forms(master_index_file, sp500_ciks, start_year=2018, end_year=2022)

#     print(f"Expected to download approximately 10,000 filings. Downloaded: {total_filings}")

#     # Step 5: Check the total number of downloaded files in the 'downloads' folder
#     total_downloaded = check_downloaded_files()

#     print(f"Final number of downloaded files: {total_downloaded}")

   
