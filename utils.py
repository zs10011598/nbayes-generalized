import os
import psycopg2
import pandas as pd
from sqlalchemy import create_engine
import numpy as np



dbname = os.environ['DBNAME']
dbuser = os.environ['DBUSER']
dbpass = os.environ['DBPASS']
dbport = os.environ['DBPORT']
dbhost = os.environ['DBHOST']


def get_initial_partitions(s_n):
	if len(s_n) == 0:
		return [[]]
	else:
		x = s_n[0]
		subs_n = s_n.copy()
		subs_n.remove(x)
		partitions = get_initial_partitions(subs_n)
		response = []
		for partition in partitions:
			response += [[[x]] + partition]
			for s in partition:
				subpartition = partition.copy()
				subpartition.remove(s)
				response += [[s+[x]] + subpartition]
	return response


def get_all_partitions():
	s_n = [i for i in range(1, 11)]
	partitions = get_initial_partitions(s_n)
	index = 0
	f = open('./data/partitions_10.csv', 'w')
	for partition in partitions:
		f.write(str(partition)+'\n')
		index += 1
	f.close()
	
	for i in range(11, 15):
		fn = open('./data/partitions_{0}.csv'.format(i), 'w')
		fp = open('./data/partitions_{0}.csv'.format(i-1), 'r')
		while True:
			line = fp.readline()
			if not line:
				break
			partition = eval(line)
			for s in partition:
				subpartition = partition.copy()
				subpartition.remove(s)
				fn.write(str([s+[i]] + subpartition)+'\n')
			fn.write(str([[i]] + partition)+'\n')
		fp.close()
		fn.close()


def db_connection():
	conn = psycopg2\
		.connect("dbname={0} user={1} password={2} port={3} host={4}"\
		.format(dbname, dbuser, dbpass, dbport, dbhost))
	conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
	return conn


def fetch_db_data(date_initial, date_final):
	conn_string = 'postgresql://{dbuser}:{dbpass}@{dbhost}:{dbport}/{dbname}'\
		.format(dbuser=dbuser, dbpass=dbpass, dbhost=dbhost, dbport=dbport, dbname=dbname)
	engine = create_engine(conn_string)
	sql_statement = """SELECT sexo, fecha_def, intubado, neumonia, edad, embarazo,\
		diabetes, epoc, asma, inmusupr, hipertension, cardiovascular, obesidad,\
		renal_cronica, tabaquismo, clasificacion_final, gridid_mun\
		FROM occurrence WHERE date_occurrence >= '{0}' AND date_occurrence <= '{1}'"""\
		.format(date_initial, date_final)
	return pd.read_sql(sql_statement, engine)


def process_age(age):
	if age < 18:
		return '0-17'
	elif age < 30:
		return '18-29'
	elif age < 40:
		return '30-39'
	elif age < 50:
		return '40-49'
	elif age < 60:
		return '50-59'
	else:
		return '60ymas'


def calculate_n_posibilities(map_values, multi_index):
	n_posibilities = 1
	for mi in multi_index:
		n_posibilities *= len(map_values[mi])
	return n_posibilities


def next_multi_index_value(values_indexes, map_values, multi_index):
	last_index = len(values_indexes)-1
	values_indexes[last_index] = (values_indexes[last_index] + 1) \
		% len(map_values[multi_index[last_index]])
	while values_indexes[last_index] == 0 and last_index > 0:
		last_index -= 1
		values_indexes[last_index] = (values_indexes[last_index] + 1) \
			% len(map_values[multi_index[last_index]])
	return values_indexes


def calcule_covars(df, variables, map_values, partition, N, NC, N_C):
	
	#print(len(variables), partition)
	#print(map_values)
	result = {}
	result['variable'] = [] 
	result['values'] = [] 
	result['epsilon'] = []
	result['score'] = []
	result['s_0'] = []
	result['N'] = [] 
	result['NC'] = []
	result['N_C'] = []
	result['Nxi'] = []
	result['NxiC'] = []
	result['Nxi_C'] = []
	result['PxiC'] = []
	result['Pxi_C'] = []
	print(partition)
	#print(variables)

	multi_indexes = []
	for s in partition:
		multi_index = []
		for index in s:
			multi_index.append(variables[index-1])
		multi_indexes.append(multi_index)
	print(multi_indexes)

	for multi_index in multi_indexes:
		
		n_posibilities = calculate_n_posibilities(map_values, multi_index)
		values_indexes = [0 for i in range(len(multi_index))]
		
		for k in range(n_posibilities):
			
			values = []
			for i in range(len(multi_index)):
				variable = multi_index[i]
				value_index = values_indexes[i]
				values.append(map_values[variable][value_index])
			
			print(multi_index, values, values_indexes)
			d = df[df[multi_index[0]] == values[0]]
			for j in range(1, len(multi_index)):
				d = d[d[multi_index[j]] == values[j]]
				if d.shape[0] <= 0:
					break
			Nxi = d.shape[0]
			PC = NC / N
			P_C = N_C / N
			s_0 = np.log(PC / P_C)
			d = d[d['target'] ==  True]
			NxiC = d.shape[0]

			if Nxi == 0:
				values_indexes = next_multi_index_value(values_indexes, \
					map_values, multi_index)
				continue
			
			Nxi_C = Nxi - NxiC
			PxiC = NxiC / NC
			Pxi_C = Nxi_C / N_C
			#score = np.log(PxiC / Pxi_C)
			score = np.log(((NxiC + 0.000005)/(NC + 0.00001))/((Nxi_C + 0.00001)/(N_C+0.000005)))
			PCxi = NxiC / Nxi
			epsilon = (Nxi*(PCxi - PC))/(Nxi*PC*P_C)**(0.5)

			result['variable'].append('|'.join(multi_index))
			result['values'].append('|'.join(values))
			result['N'].append(N)
			result['NC'].append(NC)
			result['N_C'].append(N_C)
			result['Nxi'].append(Nxi)
			result['NxiC'].append(NxiC)
			result['Nxi_C'].append(Nxi_C)
			result['PxiC'].append(PxiC)
			result['Pxi_C'].append(Pxi_C)
			result['epsilon'].append(epsilon)
			result['score'].append(score)
			result['s_0'].append(s_0)

			values_indexes = next_multi_index_value(values_indexes, \
				map_values, multi_index)

	df = pd.DataFrame(result)
	if len(partition) == 15:
		df.to_csv('./results/covars-naive-bayes.csv'\
			, index=False)
	else:
		df.to_csv('./results/covars-' + str(partition).replace(' ', '') + '.csv'\
			, index=False)
	print('-----------------------------------')


def process_data(df):
	df['target'] = df['fecha_def'].apply(lambda x: False if x == '9999-99-99' else True)
	df['edad'] = df['edad'].apply(lambda x: process_age(x))
	df['gridid_mun'] = df['gridid_mun'].apply(lambda x: str(x).zfill(5))
	df = df.drop(columns=['fecha_def', 'clasificacion_final'])
	return df