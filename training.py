import os
import time
import pandas as  pd
from utils import *



fetch_data = False

# Getting data
date_initial = '2021-07-01'
date_final = '2021-07-31'

if fetch_data:
	df = fetch_db_data(date_initial, date_final)
	df = df.sample(frac=1)
	df.to_csv('./data/occurrence.csv', index=False)
	N_training = int(df.shape[0]*0.7)
	df.iloc[0:N_training].to_csv('./data/data_training.csv', index=False)
	df.iloc[N_training:df.shape[0]].to_csv('./data/data_validation.csv', index=False)

# Processing data for death as target
df = pd.read_csv('./data/data_training.csv')
df['target'] = df['fecha_def'].apply(lambda x: False if x == '9999-99-99' else True)
df['edad'] = df['edad'].apply(lambda x: process_age(x))
df['gridid_mun'] = df['gridid_mun'].apply(lambda x: str(x).zfill(5))
df = df.drop(columns=['fecha_def', 'clasificacion_final'])

N = df.shape[0]
NC = df[df['target'] == True].shape[0]
N_C = N - NC
print(N, NC, N_C)

# Getting possible values for each variable
variables = list(df.columns)
map_values = {}
for variable in variables:
	map_values[variable] = df[variable].unique().tolist()
 
f = open('./data/partitions_14.csv', 'r')
while True:
	line = f.readline()
	if not line:
		break
	partition = eval(line)
	if 'covars-' + str(partition).replace(' ', '') + '.csv' in os.listdir('./results/'):
		continue
	# Generating 15-length partitions
	#new_partition = [[15]] + partition
	calcule_covars(df, variables, map_values, partition, N, NC, N_C)
	"""for s in partition:
					subpartition = partition.copy()
					subpartition.remove(s)
					new_partition = [s+[15]] + subpartition
					calcule_covars(df, variables, map_values, new_partition, N, NC, N_C)"""

f.close()