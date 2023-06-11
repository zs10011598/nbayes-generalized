import os
import time
import pandas as pd
from utils import *



results_files = os.listdir('./results/')
dfv = pd.read_csv('./data/data_validation.csv')
dfv = process_data(dfv)

for results_file in  results_files:
	print('------------------', results_file, '------------------')
	df = pd.read_csv('./results/' + results_file)
	s0 = df.iloc[0].s_0
	scores = []
	for i, rowv in dfv.iterrows():
		score = s0
		xis = df['variable'].unique().tolist()
		for xi in xis:
			variables = xi.split('|')
			values = []
			for variable in variables:
				values.append(str(rowv[variable]))
			values = '|'.join(values)
			try:
				score += df[(df['variable'] == xi) & (df['values'] == values)].iloc[0].score
			except Exception as e:
				print(str(e), xi, values)
		scores.append(scores)
	dfv[results_file] = scores
	print('------------------ saving file ------------------')
	dfv.to_csv('./data/data_validation_scores.csv', index=False)
	dfv.drop(columns=[results_file])
