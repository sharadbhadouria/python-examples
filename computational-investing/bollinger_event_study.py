
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

def get_bollinger_band(na_price, ldt_timestamps):
	na_mid = pd.rolling_mean(na_price, window=20)
	na_std = pd.rolling_std(na_price, window=20)

	upper = na_mid + na_std
	lower = na_mid - na_std

	# Normalize Bollinger Bands
	na_bollinger = (na_price - na_mid)/na_std
	na_ts = np.array(ldt_timestamps)
	na_ts_bollinger = pd.DataFrame(index=na_ts, data=na_bollinger)
	return na_ts_bollinger

def find_events(ls_symbols, na_ts_bollinger):
	ldt_timestamps = na_ts_bollinger.index

	# df_events = pd.DataFrame(index=ldt_timestamps, columns=ls_symbols[:-1])
	df_events = copy.deepcopy(na_ts_bollinger)
	df_events = df_events * np.NAN
	count = 0
	for sym in ls_symbols:
		for i in range(1, len(ldt_timestamps)):
			bol_val_today = na_ts_bollinger[sym].ix[ldt_timestamps[i]]
			bol_val_yest = na_ts_bollinger[sym].ix[ldt_timestamps[i-1]]
			bol_val_spx = na_ts_bollinger['SPY'].ix[ldt_timestamps[i]]

			if bol_val_today <= -2.0 and bol_val_yest >= -2.0 and bol_val_spx >= 1.0:
				df_events[sym].ix[ldt_timestamps[i]] = 1
				count += 1
	print "count: {}".format(count)
	return df_events

def main(start_date, end_date):
	
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

	na_ts_bollinger = get_bollinger_band(d_data['close'], ldt_timestamps)

	df_events = find_events(ls_symbols, na_ts_bollinger)
	# print df_events['SPY']
	print "Creating Study"
	ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
                s_filename='BollingerEventStudy.pdf', b_market_neutral=True, b_errorbars=True,
                s_market_sym='SPY')

if __name__ == '__main__':
	start_date = dt.datetime.strptime(sys.argv[1],'%m-%d-%Y')
	end_date = dt.datetime.strptime(sys.argv[2],'%m-%d-%Y')

	main(start_date, end_date)
