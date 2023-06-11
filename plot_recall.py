import pandas as pd
import numpy as np
import matplotlib.pyplot as plt



dfv = pd.read_csv('./data/data_validation.csv')
N = dfv.shape[0]
NC = dfv[dfv['target'] == True].shape[0]
columns = dfv.columns.tolist()
columns = ['target'] + [column for column in columns if 'covars-' in column]
dfv = dfv[columns]
columns = [column for column in columns if 'covars-' in column]
for column in columns:
	dfv = dfv.sort_values(by=column, ascending=False)
	recall = []
	for i in range(10):
		d = dfv.iloc[int(i*N/10): int((i+1)*N/10)]
		NCd = d[d['target'] == True]
		recall.append(NCd/NC)
	bins = [i for i in range(11, 1)]
	plt.plot(bins, recall)
	plt.xlabel('Deciles')
	plt.ylabel('Recall')
	plt.savefig('./recall_plots/{0}.png'.format(column.split('.')[0]))