import sys
from sys import exit
import vectors
# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

# Third Party Imports
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

import optimizer


def main(start_date, end_date, symbols):
	ldt_timestamps, na_price = optimizer.get_close_price_for_symbols(start_date, 
		end_date, symbols)

	na_mid = pd.rolling_mean(na_price, window=20)
	na_std = pd.rolling_std(na_price, window=20)

	upper = na_mid + na_std
	lower = na_mid - na_std

	# Normalize Bollinger Bands
	na_bollinger = (na_price - na_mid)/na_std
	na_ts = np.array(ldt_timestamps)
	na_ts_bollinger = np.column_stack((na_ts.flat, na_bollinger.flat))

	upper_boundary = np.ones(upper.shape)
	lower_boundary = -upper_boundary

	# Plot bands
	plt.clf()
	fig = plt.figure(1)
	ax1 = fig.add_subplot(211)

	for i in range(len(symbols)):
		label = symbols[i]
		ax1.plot(ldt_timestamps, na_price[:, i], label=label, alpha=0.4)

	ax1.plot(ldt_timestamps, na_mid, label="SMA")
	ax1.plot(ldt_timestamps, upper, label="Upper Bollinger")
	ax1.plot(ldt_timestamps, lower, label="Lower Bollinger")

	ax1.set_ylabel('Adjusted Close')
	ax1.set_xlabel('Date')
	plt.setp(ax1.get_xticklabels(), rotation=45)

	box = ax1.get_position()
	ax1.set_position([box.x0, box.y0, box.width * 0.8, box.height])

	# Put a legend to the right of the current axis
	ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5))

	ax2 = fig.add_subplot(212)

	ax2.plot(ldt_timestamps, na_bollinger)
	ax2.plot(ldt_timestamps, upper_boundary)
	ax2.plot(ldt_timestamps, lower_boundary)

	ax2.set_ylabel('Bollinger Feature')
	ax2.set_xlabel('Date')
	plt.setp(ax2.get_xticklabels(), rotation=45)
	
	plt.show()

	return na_ts_bollinger


if __name__ == '__main__':
	start_date = dt.datetime.strptime(sys.argv[1],'%m-%d-%Y')
	end_date = dt.datetime.strptime(sys.argv[2],'%m-%d-%Y')

	main(start_date, end_date, sys.argv[3:])