import sys
import csv
import pandas as pd
import numpy as np
import math
import copy
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep

import bollinger_event_study
import marketsim
import analyze

def main(starting_cash, start_date, end_date, order_file, value_file):
	print "Starting Cash: {}".format(starting_cash)
	print "Start date: {} End Date: {}".format(start_date, end_date)
	print "Order File: {} Value File: {}".format(order_file, value_file)

	dataobj = da.DataAccess('Yahoo')
	ls_symbols = dataobj.get_symbols_from_list('sp5002012')
	ls_symbols.append('SPY')
	# ls_symbols.append('$SPX')
	
	ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
	ldt_timestamps = du.getNYSEdays(start_date, end_date, dt.timedelta(hours=16))

	ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
	d_data = dict(zip(ls_keys, ldf_data))

	for s_key in ls_keys:
		d_data[s_key] = d_data[s_key].fillna(method='ffill')
		d_data[s_key] = d_data[s_key].fillna(method='bfill')
		d_data[s_key] = d_data[s_key].fillna(1.0)

	na_ts_bollinger = bollinger_event_study.get_bollinger_band(d_data['close'], ldt_timestamps)

	# df_events = bollinger_event_study.find_events(ls_symbols, na_ts_bollinger)

	# print "Creating Study"
	# ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
 #                s_filename='BollingerEventStudy.pdf', b_market_neutral=True, b_errorbars=True,
 #                s_market_sym='SPY')
	# ldt_timestamps = na_ts_bollinger.index

	# print len(ldt_timestamps)
	count = 0
	with open(order_file, 'wb') as outfile:
		writer = csv.writer(outfile, delimiter=',')
		for sym in ls_symbols:
			for i in range(1, len(ldt_timestamps)):
				bol_val_today = na_ts_bollinger[sym].ix[ldt_timestamps[i]]
				bol_val_yest = na_ts_bollinger[sym].ix[ldt_timestamps[i-1]]
				bol_val_spx = na_ts_bollinger['SPY'].ix[ldt_timestamps[i]]

				if bol_val_today < -2.0 and bol_val_yest >= -2.0 and bol_val_spx >= 1.3:
					out_data = generate_output_data(ldt_timestamps[i], sym)
					writer.writerow(out_data)
					end_ts = ldt_timestamps[i]
					if i < len(ldt_timestamps) - 5:
						end_ts = ldt_timestamps[i+5]
					else:
						end_ts = ldt_timestamps[-1]
					out_data = generate_output_data(end_ts, sym, buy=False)
					writer.writerow(out_data)
					count += 1

	print "Number of events: {}".format(count)
	print "Performing fund simulation..."
	marketsim.main(starting_cash, order_file, value_file)
	print "Analyzing fund..."
	analyze.main(value_file, '$SPX')

def generate_output_data(timestamp, symbol, buy=True):
	out_data = []
	out_data.append(timestamp.year)
	out_data.append(timestamp.month)
	out_data.append(timestamp.day)
	out_data.append(symbol)
	out_data.append('Buy' if buy else 'Sell')
	out_data.append(100)

	return out_data


if __name__ == '__main__':
	start_date = dt.datetime.strptime(sys.argv[2],'%m-%d-%Y')
	end_date = dt.datetime.strptime(sys.argv[3],'%m-%d-%Y')
	main(int(sys.argv[1]), start_date, end_date, sys.argv[4], sys.argv[5])

