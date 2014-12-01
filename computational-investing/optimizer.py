
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

def simulate(start_date, end_date, symbols, allocation):
	if np.floor(sum(allocation)) > 1.0:
		print "Invalid allocation. Expected total: 1.0 Got allocation {} with sum: {}".format(
			allocation, sum(allocation))
		return

	ldt_timestamps, na_price = get_close_price_for_symbols(start_date, end_date, symbols)
	na_normalized_price = na_price / na_price[0, :]

	na_alloc = na_normalized_price * allocation
	all_sum_daily = np.sum(na_alloc, 1)

	daily_ret = tsu.returnize0(all_sum_daily.copy())
	avg_daily_ret = np.mean(daily_ret)
	std_dev = np.std(daily_ret)
	sharpe = np.sqrt(252) * avg_daily_ret/std_dev
	cum_ret = all_sum_daily[-1]/all_sum_daily[0]

	return std_dev, avg_daily_ret, sharpe, cum_ret


def get_close_price_for_symbols(start_date, end_date, symbols):
	dt_timeofday = dt.timedelta(hours=16)
	ldt_timestamps = du.getNYSEdays(start_date, end_date, dt_timeofday)

	# Local copy of Yahoo data, doesn't go to Yahoo to get data
	c_dataobj = da.DataAccess('Yahoo', cachestalltime=0)
	ldf_data = c_dataobj.get_data(ldt_timestamps, symbols, 'close')
	ldf_data.fillna(method='ffill')
	ldf_data.fillna(method='bfill')
	ldf_data.fillna(1.0)
	return ldt_timestamps, ldf_data.values


def compare_symbols(start_date, end_date, symbols, optimal_allocations, show=False):

	symbols.append('$SPX')
	ldt_timestamps, na_price = get_close_price_for_symbols(start_date, end_date, symbols)
	daily_rets = tsu.returnize0(na_price.copy())
	# Estimate total portfolio returns
	# print daily_rets[:, 0:-1].shape
	na_portrets = np.sum(daily_rets[:, 0:-1] * optimal_allocations, axis=1)
	na_port_total = np.cumprod(na_portrets + 1)
	na_component_total = np.cumprod(daily_rets[:,0:-1] + 1, axis=0)
	spx_cum_ret = np.cumprod(daily_rets[:, -1] + 1, axis=0)

	# Plot of portfolio vs spx
	plt.clf()
	fig = plt.figure(1)
	ax = plt.subplot(111)

	for i in range(len(symbols) - 1):
		label = symbols[i]
		plt.plot(ldt_timestamps, na_component_total[:, i], label=label, alpha=0.4)

	plt.plot(ldt_timestamps, na_port_total, label='Portfolio')
	plt.plot(ldt_timestamps, spx_cum_ret, label='S&P500')

	plt.ylabel('Cumulative Returns')
	plt.xlabel('Date')
	fig.autofmt_xdate(rotation=45)
	
	box = ax.get_position()
	ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

	# Put a legend to the right of the current axis
	ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
	if show:
		plt.show()
	else:
		plt.savefig('portfolio-comparison.pdf', format='pdf')


def main(start_year, start_month, start_day, end_year, end_month, end_day, symbols):
	optimal_allocations = []
	best_sharpe = best_vol = best_mean = best_cum = 0.0

	allocation = np.zeros(len(symbols))
	start_date = dt.datetime(start_year, start_month, start_day)
	end_date = dt.datetime(end_year, end_month, end_day)

	for vec in vectors.vectors(len(symbols), 10):
		allocation = [v/10.0 for v in vec];
		vol, daily_ret, sharpe, cum_ret = simulate(start_date, end_date, symbols, allocation)
		# print "Allocation: {}".format(allocation);
		# print "New sharpe: {}".format(sharpe)
		if (sharpe > best_sharpe):
			optimal_allocations = allocation
			best_sharpe = sharpe
			best_vol = vol
			best_mean = daily_ret
			best_cum = cum_ret

	print "Start Date: {}".format(start_date)
	print "End Date: {}".format(end_date)
	print "Optimal Allocations: {}".format(optimal_allocations)
	print "Sharpe Ratio: {}".format(best_sharpe)
	print "Volatility (stddev of daily returns): {}".format(best_vol)
	print "Average daily Return: {}".format(best_mean)
	print "Cummulative Return: {}".format(best_cum)

	spx_vol, spx_daily_ret, spx_sharpe, spx_cum_ret = simulate(start_date, end_date, ['$SPX'], [1.0])
	print "SP-500 Sharpe Ratio: {}".format(spx_sharpe)
	print "SP-500 Volatility (stddev of daily returns): {}".format(spx_vol)
	print "SP-500 Average daily Return: {}".format(spx_daily_ret)
	print "SP-500 Cummulative Return: {}".format(spx_cum_ret)
	compare_symbols(start_date, end_date, symbols, optimal_allocations, True)
	

if __name__ == '__main__':
	main(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), 
		int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6]), sys.argv[7:])
