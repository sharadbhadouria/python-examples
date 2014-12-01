import sys
import pandas as pd
import numpy as np
import math
import copy
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep
	

def find_events(ls_symbols, close_price_data):

	# Creating an empty dataframe
	df_events = copy.deepcopy(close_price_data)
	df_events = df_events * np.NAN

	# Time stamps for the event range
	ldt_timestamps = close_price_data.index
	for sym in ls_symbols:
		for i in range(1, len(ldt_timestamps)):
			price_today = close_price_data[sym].ix[ldt_timestamps[i]]
			price_yest = close_price_data[sym].ix[ldt_timestamps[i-1]]
			
			if price_yest >= 8.0 and price_today < 8.0:
				df_events[sym].ix[ldt_timestamps[i]] = 1

  	return df_events


def main(start_date, end_date):
	ldt_timestamps = du.getNYSEdays(start_date, end_date, dt.timedelta(hours=16))

	dataobj = da.DataAccess('Yahoo')
	ls_symbols = dataobj.get_symbols_from_list('sp5002012')
	ls_symbols.append('SPY')
	
	ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
	ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
	d_data = dict(zip(ls_keys, ldf_data))

	for s_key in ls_keys:
		d_data[s_key] = d_data[s_key].fillna(method='ffill')
		d_data[s_key] = d_data[s_key].fillna(method='bfill')
		d_data[s_key] = d_data[s_key].fillna(1.0)

	df_events = find_events(ls_symbols, d_data['actual_close'])
	print type(df_events)

	print "Creating Study"
	ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
                s_filename='MyEventStudy.pdf', b_market_neutral=True, b_errorbars=True,
                s_market_sym='SPY')


if __name__ == '__main__':
	start_year = int(sys.argv[1])
	start_mth = int(sys.argv[2])
	start_day = int(sys.argv[3])
	end_year = int(sys.argv[4])
	end_mth = int(sys.argv[5])
	end_day = int(sys.argv[6])

	start_date = dt.datetime(start_year, start_mth, start_day)
	end_date = dt.datetime(end_year, end_mth, end_day)
	main(start_date, end_date)
	

   