import matplotlib.pyplot as plt
import pandas as pd


df = pd.read_csv('all_moves.csv', sep=';')
print('move distribution by tier:')
print(df.value_counts('tier'))
df.value_counts('tier').sort_index().plot(kind='bar', x=sorted(df.tier))
plt.show()
