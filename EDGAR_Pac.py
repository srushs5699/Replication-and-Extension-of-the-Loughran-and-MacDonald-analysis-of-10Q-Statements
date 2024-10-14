# #!/usr/bin/python3
# """
#     Utility programs for accessing SEC/EDGAR
#     ND-SRAF / McDonald : 201606
#     https.//sraf.nd.edu
# """

# import time
# from urllib.request import urlopen
# from zipfile import ZipFile
# from io import BytesIO
# from datetime import datetime as dt
# import pytz

# def download_masterindex(year, qtr, flag=False):
#     # Download Master.idx from EDGAR
#     # Loop accounts for temporary server/ISP issues
#     # ND-SRAF / McDonald : 201606


#     number_of_tries = 4
#     sleep_time = 10  # Note sleep time accumulates according to err


#     PARM_ROOT_PATH = 'https://www.sec.gov/Archives/edgar/full-index/'

#     start = time.process_time()  # Note: using clock time not CPU
#     masterindex = []
#     #  using the zip file is a little more complicated but orders of magnitude faster
#     append_path = str(year) + '/QTR' + str(qtr) + '/master.idx'  # /master.idx => nonzip version
#     sec_url = PARM_ROOT_PATH + append_path
#     print("going from here")
#     print(sec_url)
#     for i in range(1, number_of_tries + 1):
#         try:
#             zipfile = ZipFile(BytesIO(urlopen(sec_url).read()))
#             # records = zipfile.open('master.idx').read().decode('utf-8', 'ignore').splitlines()[10:]
#             records = urlopen(sec_url).read().decode('utf-8').splitlines()[10:] #  => nonzip version
#             break
#         except Exception as exc:
#             if i == 1:
#                 print('\nError in download_masterindex')
#             print('  {0}. _url:  {1}'.format(i, sec_url))

#             print('  Warning: {0}  [{1}]'.format(str(exc), time.strftime('%c')))
#             if '404' in str(exc):
#                 break
#             if i == number_of_tries:
#                 return False
#             print('     Retry in {0} seconds'.format(sleep_time))
#             time.sleep(sleep_time)
#             sleep_time += sleep_time


#     # Load m.i. records into masterindex list
#     for line in records:
#         mir = MasterIndexRecord(line)
#         if not mir.err:
#             masterindex.append(mir)

#     if flag:
#         print('download_masterindex:  ' + str(year) + ':' + str(qtr) + ' | ' +
#               'len() = {:,}'.format(len(masterindex)) + ' | Time = {0:.4f}'.format(time.process_time() - start) +
#               ' seconds')

#     return masterindex


# class MasterIndexRecord:
#     def __init__(self, line):
#         self.err = False
#         parts = line.split('|')
#         if len(parts) == 5:
#             self.cik = int(parts[0])
#             self.name = parts[1]
#             self.form = parts[2]
#             self.filingdate = int(parts[3].replace('-', ''))
#             self.path = parts[4]
#         else:
#             self.err = True
#         return


# def edgar_server_not_available(flag=False):
#     # routine to run download only when EDGAR server allows bulk download.
#     # see:  https://www.sec.gov/edgar/searchedgar/ftpusers.htm
#     # local time is converted to EST for check


#     SERVER_BGN = 21  # Server opens at 9:00PM EST
#     SERVER_END = 6   # Server closes at 6:00AM EST

#     # Get UTC time from local and convert to EST
#     utc_dt = pytz.utc.localize(dt.utcnow())
#     est_timezone = pytz.timezone('US/Eastern')
#     est_dt = est_timezone.normalize(utc_dt.astimezone(est_timezone))
#     return False
#     if est_dt.hour >= SERVER_BGN or est_dt.hour < SERVER_END:
#         return False
#     else:
#         if flag:
#             print('\rSleeping: ' + str(dt.now()), end='', flush=True)
#         time.sleep(6)  # Sleep for 10 minutes
#         return True

# EDGAR_Pac.py

import os
import requests
import pandas as pd

# Define MASTERINDEX class
class MASTERINDEX:
    def __init__(self, cik, name, form, filing_date, path):
        self.cik = cik
        self.name = name
        self.form = form
        self.filing_date = filing_date
        self.path = path

# Function to download index files from SEC's EDGAR
def download_index_files(years, quarters):
    base_url = "https://www.sec.gov/Archives/edgar/full-index"
    headers = {
        'User-Agent': 'Srushti (srushtishinde12@gmail.com)',
        'Accept-Encoding': 'gzip, deflate',
        'Host': 'www.sec.gov'
    }
    for year in years:
        for quarter in quarters:
            url = f"{base_url}/{year}/QTR{quarter}/master.idx"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                directory = f"index_files/{year}/QTR{quarter}"
                os.makedirs(directory, exist_ok=True)
                with open(f"{directory}/master.idx", "wb") as f:
                    f.write(response.content)
                print(f"Downloaded {year} QTR{quarter} index file")
            else:
                print(f"Failed to download {year} QTR{quarter} index file. Status code: {response.status_code}")

# Function to parse and consolidate the master index into a CSV file
def consolidate_master_index(years, quarters):
    entries = []
    for year in years:
        for quarter in quarters:
            file_path = f"index_files/{year}/QTR{quarter}/master.idx"
            try:
                with open(file_path, 'r', encoding='latin1') as file:
                    lines = file.readlines()
                    # Skip the header lines (first 10 lines)
                    records = lines[11:]  # Adjust the index if necessary
                    for record in records:
                        parts = record.strip().split('|')
                        if len(parts) == 5:
                            entries.append({
                                'cik': parts[0].strip(),
                                'name': parts[1].strip(),
                                'form': parts[2].strip(),
                                'filing_date': parts[3].strip(),
                                'path': parts[4].strip()
                            })
            except FileNotFoundError:
                print(f"{file_path} not found")
        print(f"Processed index files for {year}")

    df = pd.DataFrame(entries)
    df.to_csv('master_index.csv', index=False)
    print("Consolidated master index created")

# Main function to trigger downloading and consolidating
if __name__ == '__main__':
    years = range(2019, 2024)  # Example range of years
    quarters = range(1, 5)  # Quarters (1, 2, 3, 4)

    # Step 1: Download the index files for given years and quarters
    download_index_files(years, quarters)

    # Step 2: Consolidate the downloaded index files into a master index CSV
    consolidate_master_index(years, quarters)

    print("Index download and consolidation completed.")
