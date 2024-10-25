"""
Script for creating plot of evolution results.
"""

import json
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd

df_dict = {'n_actions': [], '%_pareto_front_found_in_500_gens': []}
trial_counts = {}
with open('evolution_results.csv', 'r') as f:
    for line in f:
        data = line.split(',', maxsplit=2)
        n_actions = int(data[0])
        still_to_find = data[2].count('(')
        if n_actions not in trial_counts:
            trial_counts[n_actions] = 0
        if trial_counts[n_actions] < 100:
            trial_counts[n_actions] += 1
            df_dict['n_actions'].append(n_actions)
            percent_to_find = 100 * ((11 - still_to_find) / 11.)
            df_dict['%_pareto_front_found_in_500_gens'].append(percent_to_find)
df = pd.DataFrame(df_dict)
means=df.groupby('n_actions')['%_pareto_front_found_in_500_gens'].mean()
medians=df.groupby('n_actions')['%_pareto_front_found_in_500_gens'].median()
sns.boxplot(data=df, x='n_actions', y='%_pareto_front_found_in_500_gens', color='lightsteelblue')
sns.lineplot(y=means.values,x=np.arange(9), color='black', lw=1, linestyle='dashed', label='mean')
sns.scatterplot(y=medians.values,x=np.arange(9), color='black', label='median')
plt.legend()
plt.yticks(np.linspace(0, 100, 12))
plt.title('% of Pareto front found by Evolution in 500 gens')
plt.savefig('evolution_plot.pdf')
plt.show()
