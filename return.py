import numpy as np
import pandas as pd
import os


tfidf_matrix = np.load('./matrix/tfidf_matrix.npy')
tfidf_matrix = np.mean(tfidf_matrix, axis=1, keepdims=True)
returns_df = pd.read_csv('cumulative_excess_returns.csv')


returns_df['filing_date'] = pd.to_datetime(returns_df['filing_date'])
cik_to_return = {
    (str(row['cik']), row['filing_date']): row['cumulative_excess_return']
    for _, row in returns_df.iterrows()
}


cleaned_dir = './cleaned'
returns_matrix = []


for filename in os.listdir(cleaned_dir):
    if filename.endswith('.txt'):
        cik, filing_date_str = filename.split('_')[:2]
        filing_date = pd.to_datetime(filing_date_str)
        return_value = cik_to_return.get((cik, filing_date), 0)
        returns_matrix.append(return_value)


returns_matrix = np.array(returns_matrix).reshape(-1, 1)
tfidf_returns = np.column_stack((tfidf_matrix, returns_matrix))
np.save('./matrix/tfidf_returns.npy', tfidf_returns)
