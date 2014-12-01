import sys
import csv

# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

# Third Party Imports
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def main(cash, order_file, value_file):
	# Reading the orders

	trades = pd.read_csv(order_file, parse_dates=[[0, 1, 2]], header=None, index_col=[0])
	trades.sort_index(inplace=True)

	symbols = list(set(trades.iloc[:, 0]))
	sorted_dates = trades.index
	start_date = sorted_dates[0]
	end_date = sorted_dates[-1] + dt.timedelta(days=1)

	# Read adjusted close value for symbols
	dt_timeofday = dt.timedelta(hours=16)
	ldt_timestamps = du.getNYSEdays(start_date, end_date, dt_timeofday)
	# Local copy of Yahoo data, doesn't go to Yahoo to get data
	c_dataobj = da.DataAccess('Yahoo')
	ldf_data = c_dataobj.get_data(ldt_timestamps, symbols, 'close')
	ldf_data.fillna(method='ffill')
	ldf_data.fillna(method='bfill')
	ldf_data.fillna(1.0)

	df_cash_table = pd.DataFrame(index=ldt_timestamps, columns=['_CASH'])
	df_cash_table = df_cash_table.fillna(0)
	# Initiating cash
	df_cash_table.loc[str(start_date + dt.timedelta(hours=16))] = cash

	df_trade_matrix = pd.DataFrame(index=ldt_timestamps, columns=symbols)
	df_trade_matrix = df_trade_matrix.fillna(0.0)

	for date_key, entry in trades.iterrows():
		# date = dt.datetime(int(entry[0]), int(entry[1]), int(entry[2]))
		date_key = str(date_key + dt.timedelta(hours=16))
		num_units = int(entry.iloc[2])
		symbol = entry.iloc[0]
		cost = ldf_data.loc[date_key][symbol] * num_units
		if entry.iloc[1] == 'Buy':
			cost = -cost
		else:
			num_units = -num_units
		df_trade_matrix.loc[date_key][symbol] += num_units
		# Add the value to exiting cash, since there can be muliple transanctions on the same day
		df_cash_table.loc[date_key] = df_cash_table.loc[date_key] + cost

	# carry over owned stock units till sold
	df_trade_matrix =  np.cumsum(df_trade_matrix,axis=0)
	df_cash_table = np.cumsum(df_cash_table, axis=0)
	print "Trade Matrix: \n{} ".format(df_trade_matrix)
	print "Cash Table: \n{}".format(df_cash_table)

	# Compute the holding equity value for each date
	df_holding_matrix = pd.DataFrame(index=ldt_timestamps, columns=symbols)
	df_holding_matrix = df_holding_matrix.fillna(0.0)
	for date_key, row in df_holding_matrix.iterrows():
		for symbol in symbols:
			close_price = ldf_data.loc[date_key][symbol]
			num_units = df_trade_matrix.loc[date_key][symbol]
			df_holding_matrix.loc[date_key][symbol] = close_price * num_units

	
	# Add cash component to the holding matrix
	df_holding_matrix['_CASH'] = df_cash_table['_CASH']
	print "Holding Matrix: \n{}".format(df_holding_matrix)	

	df_value = np.sum(df_holding_matrix, axis=1)
	print df_value.index
	print "Total Value: \n{}".format(df_value)
	
	# Write to csv
	# df_value.to_csv(value_file, header=False, date_format='%Y,%m,%d')
	with open(value_file, 'wb') as out_file:
		writer = csv.writer(out_file, delimiter=',')
		for val_idx in df_value.index:
			out_data = []
			out_data.append(val_idx.year)
			out_data.append(val_idx.month)
			out_data.append(val_idx.day)
			out_data.append(df_value[val_idx])
			writer.writerow(out_data)


if __name__ == '__main__':
    main(int(sys.argv[1]), sys.argv[2], sys.argv[3])
