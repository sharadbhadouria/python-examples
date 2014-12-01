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

import marketsim
import analyze
import event_study

def main(starting_cash, start_date, end_date, order_file, value_file):
	print "Starting Cash: {}".format(starting_cash)
	print "Start date: {} End Date: {}".format(start_date, end_date)
	print "Order File: {} Value File: {}".format(order_file, value_file)

	ldt_timestamps = du.getNYSEdays(start_date, end_date, dt.timedelta(hours=16))

	dataobj = da.DataAccess('Yahoo')
	ls_symbols = dataobj.get_symbols_from_list('sp5002012')
	ls_symbols.append('$SPX')
	ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']

	ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
	d_data = dict(zip(ls_keys, ldf_data))

	for s_key in ls_keys:
		d_data[s_key] = d_data[s_key].fillna(method='ffill')
		d_data[s_key] = d_data[s_key].fillna(method='bfill')
		d_data[s_key] = d_data[s_key].fillna(1.0)

	close_price_data = d_data['actual_close']

	df_events = event_study.find_events(ls_symbols, close_price_data)

	# print "Creating Study"
	# ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
 #                s_filename='MyEventStudy.pdf', b_market_neutral=True, b_errorbars=True,
 #                s_market_sym='$SPX')

	# Time stamps for the event range
	ldt_timestamps = close_price_data.index

	with open(order_file, 'wb') as outfile:
		writer = csv.writer(outfile, delimiter=',')
		for sym in ls_symbols:
			for i in range(1, len(ldt_timestamps)):
				price_today = close_price_data[sym].ix[ldt_timestamps[i]]
				price_yest = close_price_data[sym].ix[ldt_timestamps[i-1]]
				
				if price_yest >= 7.0 and price_today < 7.0:
					out_data = generate_output_data(ldt_timestamps[i], sym)
					writer.writerow(out_data)
					end_ts = ldt_timestamps[i]
					if i > ldt_timestamps.shape:
						end_ts = ldt_timestamps[-1]
					else:
						end_ts = ldt_timestamps[i+5]
					out_data = generate_output_data(end_ts, sym, buy=False)
					writer.writerow(out_data)

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