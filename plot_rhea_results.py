"""
Script for creating plot of RHEA results.
"""

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd

df_dict = {'n_actions': [], 'gens_to_converge': []}
trial_counts = {}
with open('rhea_results.csv', 'r') as f:
    for line in f:
        data = line.split(',')
        n_actions = int(data[0])
        gens_to_converge = int(data[1])
        if n_actions not in trial_counts:
            trial_counts[n_actions] = 0
        if trial_counts[n_actions] < 100:
            trial_counts[n_actions] += 1
            df_dict['n_actions'].append(n_actions)
            df_dict['gens_to_converge'].append(gens_to_converge)
df = pd.DataFrame(df_dict)
medians=df.groupby('n_actions')['gens_to_converge'].mean()
sns.boxplot(data=df, x='n_actions', y='gens_to_converge', color='lightsteelblue')
sns.lineplot(y=medians.values,x=np.arange(9), color='black', lw=1, linestyle='dashed', label='mean')
plt.title('Time for RHEA to discover full Pareto front')
plt.savefig('rhea_plot.pdf')
plt.show()
