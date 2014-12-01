
import sys
import optimizer

import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import QSTK.qstkutil.tsutil as tsu

def main(fund_tx_file, comparision_symbol):

	fund_txn = pd.read_csv(fund_tx_file, parse_dates=[[0, 1, 2]], header=None, index_col=[0])
	fund_txn.sort_index(inplace=True)
	sorted_dates = fund_txn.index
	start_date = sorted_dates[0]
	end_date = sorted_dates[-1] + dt.timedelta(days=1)

	total_daily_rets = fund_txn.iloc[:, -1].astype('f4')
	# print total_daily_rets
	daily_ret = tsu.returnize0(total_daily_rets.copy())
	avg_daily_ret = np.mean(daily_ret)
	std_dev = np.std(daily_ret)
	sharpe = np.sqrt(252) * avg_daily_ret/std_dev
	cum_ret = total_daily_rets[-1]/total_daily_rets[0]

	comp_sym_vol, comp_sym_daily_ret, comp_sym_sharpe, comp_sym_cum_ret = optimizer.simulate(
		start_date, end_date, [comparision_symbol], [1.0])

	print("Details of the Performance of the portfolio :")
	print("Data Range : {} to {}").format(str(start_date + dt.timedelta(hours=16)), 
		str(end_date + dt.timedelta(hours=16)))

	print("Sharpe Ratio of Fund : {}").format(sharpe)
	print("Sharpe Ratio of {} : {}").format(comparision_symbol,comp_sym_sharpe)

	print("Total Return of Fund : {}").format(cum_ret)
	print("Total Return of {} : {}").format(comparision_symbol, comp_sym_cum_ret)

	print("Standard Deviation of Fund : {}").format(std_dev)
	print("Standard Deviation of {} : {}").format(comparision_symbol, comp_sym_vol)

	print("Average Daily Return of Fund : {}").format(avg_daily_ret)
	print("Average Daily Return of {} : {}").format(comparision_symbol, comp_sym_daily_ret)

	# Plot Fund vs comparing symbol
	plt.clf()
	fig = plt.figure(1)
	ax = plt.subplot(111)
	daily_ret_cummulative = np.cumprod(daily_ret + 1, axis=0)

	# Calculate daily returns for comparing symbol
	ldt_timestamps, na_price = optimizer.get_close_price_for_symbols(start_date, 
		end_date, [comparision_symbol])
	na_normalized_price = na_price / na_price[0, :]
	all_sum_daily = np.sum(na_normalized_price, 1)
	comp_sym_daily_ret = tsu.returnize0(all_sum_daily.copy())
	comp_sym_cummulative = np.cumprod(comp_sym_daily_ret + 1, axis=0)

	plt.plot(sorted_dates, daily_ret_cummulative, label='Fund', alpha=0.4)
	plt.plot(sorted_dates, comp_sym_cummulative, label=comparision_symbol)
	plt.ylabel('Cumulative Returns')
	plt.xlabel('Date')
	fig.autofmt_xdate(rotation=45)
	
	box = ax.get_position()
	ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
	# Put a legend to the right of the current axis
	ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
	plt.show()

if __name__ == '__main__':
	main(sys.argv[1], sys.argv[2])