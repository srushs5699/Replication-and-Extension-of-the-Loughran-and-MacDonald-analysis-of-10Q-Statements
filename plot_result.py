import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


tfidf_returns = np.load('./matrix/tfidf_returns.npy')
df = pd.DataFrame(tfidf_returns, columns=['tfidf', 'returns'])

# filter !=0
df_filtered = df[(df['tfidf'] != 0) & (df['returns'] != 0)].copy()

df_filtered['tfidf_quintile'] = pd.qcut(df_filtered['tfidf'], q=5, labels=['1', '2', '3', '4', '5'])
quintile_returns_median = df_filtered.groupby('tfidf_quintile', observed=True)['returns'].mean().reset_index()
quintile_returns_median['tfidf_quintile'] = quintile_returns_median['tfidf_quintile'].astype(str) + ' (Quintile)'

plt.figure(figsize=(10, 6))
plt.plot(quintile_returns_median['tfidf_quintile'], quintile_returns_median['returns'], marker='o', linestyle='-', color='b')

plt.title('Returns vs TF-IDF Quintiles (Median)')
plt.xlabel('TF-IDF Quintile')
plt.ylabel('Median Returns')
plt.xticks(rotation=45)


plt.tight_layout()
plt.show()

print(quintile_returns_median)
