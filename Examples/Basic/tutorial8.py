'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on January, 24, 2013

@author: Sourabh Bajaj
@contact: sourabhbajaj@gatech.edu
@summary: Demonstrates the use of the CVXOPT portfolio optimization call.
'''

# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

# Third Party Imports
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def getFrontier(na_data):
    '''Function gets a 100 sample point frontier for given returns'''

    # Special Case with fTarget=None, just returns average rets.
    (na_avgrets, na_std, b_error) = tsu.OptPort(na_data, None)

    # Declaring bounds on the optimized portfolio
    na_lower = np.zeros(na_data.shape[1])
    na_upper = np.ones(na_data.shape[1])

    # Getting the range of possible returns with these bounds
    (f_min, f_max) = tsu.getRetRange(na_data, na_lower, na_upper,
                            na_avgrets, s_type="long")

    # Getting the step size and list of returns to optimize for.
    f_step = (f_max - f_min) / 100.0
    lf_returns = [f_min + x * f_step for x in range(101)]

    # Declaring empty lists
    lf_std = []
    lna_portfolios = []

    # Calling the optimization for all returns
    for f_target in lf_returns:
        (na_weights, f_std, b_error) = tsu.OptPort(na_data, f_target,
                                na_lower, na_upper, s_type="long")
        lf_std.append(f_std)
        lna_portfolios.append(na_weights)

    return (lf_returns, lf_std, lna_portfolios, na_avgrets, na_std)


def main():
    '''Main Function'''

    # S&P 100
    ls_symbols = ['AAPL', 'ABT', 'ACN', 'AEP', 'ALL', 'AMGN', 'AMZN', 'APC', 'AXP', 'BA', 'BAC', 'BAX', 'BHI', 'BK', 'BMY', 'BRK.B', 'CAT', 'C', 'CL', 'CMCSA', 'COF', 'COP', 'COST', 'CPB', 'CSCO', 'CVS', 'CVX', 'DD', 'DELL', 'DIS', 'DOW', 'DVN', 'EBAY', 'EMC', 'EXC', 'F', 'FCX', 'FDX', 'GD', 'GE', 'GILD', 'GOOG', 'GS', 'HAL', 'HD', 'HNZ', 'HON', 'HPQ', 'IBM', 'INTC', 'JNJ', 'JPM', 'KFT', 'KO', 'LLY', 'LMT', 'LOW', 'MA', 'MCD', 'MDT', 'MET', 'MMM', 'MO', 'MON', 'MRK', 'MS', 'MSFT', 'NKE', 'NOV', 'NSC', 'NWSA', 'NYX', 'ORCL', 'OXY', 'PEP', 'PFE', 'PG', 'PM', 'QCOM', 'RF', 'RTN', 'SBUX', 'SLB', 'HSH', 'SO', 'SPG', 'T', 'TGT', 'TWX', 'TXN', 'UNH', 'UPS', 'USB', 'UTX', 'VZ', 'WAG', 'WFC', 'WMB', 'WMT', 'XOM']

    # Creating an object of the dataaccess class with Yahoo as the source.
    c_dataobj = da.DataAccess('Yahoo')

    ls_all_syms = c_dataobj.get_all_symbols()
    # Bad symbols are symbols present in portfolio but not in all syms
    ls_bad_syms = list(set(ls_symbols) - set(ls_all_syms))
    for s_sym in ls_bad_syms:
        i_index = ls_symbols.index(s_sym)
        ls_symbols.pop(i_index)

    # Start and End date of the charts
    dt_end = dt.datetime(2010, 1, 1)
    dt_start = dt_end - dt.timedelta(days=365)
    dt_test = dt_end + dt.timedelta(days=365)

    # We need closing prices so the timestamp should be hours=16.
    dt_timeofday = dt.timedelta(hours=16)

    # Get a list of trading days between the start and the end.
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)
    ldt_timestamps_test = du.getNYSEdays(dt_end, dt_test, dt_timeofday)

    # Reading just the close prices
    df_close = c_dataobj.get_data(ldt_timestamps, ls_symbols, "close")
    df_close_test = c_dataobj.get_data(ldt_timestamps_test, ls_symbols, "close")

    # Filling the data for missing NAN values
    df_close = df_close.fillna(method='ffill')
    df_close = df_close.fillna(method='bfill')
    df_close_test = df_close_test.fillna(method='ffill')
    df_close_test = df_close_test.fillna(method='bfill')

    # Copying the data values to a numpy array to get returns
    na_data = df_close.values.copy()
    na_data_test = df_close_test.values.copy()

    # Getting the daily returns
    tsu.returnize0(na_data)
    tsu.returnize0(na_data_test)

    # Calculating the frontier.
    (lf_returns, lf_std, lna_portfolios, na_avgrets, na_std) = getFrontier(na_data)
    (lf_returns_test, lf_std_test, unused, unused, unused) = getFrontier(na_data_test)

    # Plotting the efficient frontier
    plt.clf()
    plt.plot(lf_std, lf_returns, 'b')
    plt.plot(lf_std_test, lf_returns_test, 'r')

    # Plot where the efficient frontier would be the following year
    lf_ret_port_test = []
    lf_std_port_test = []
    for na_portfolio in lna_portfolios:
        na_port_rets = np.dot(na_data_test, na_portfolio)
        lf_std_port_test.append(np.std(na_port_rets))
        lf_ret_port_test.append(np.average(na_port_rets))

    plt.plot(lf_std_port_test, lf_ret_port_test, 'k')

    # Plot indivisual stock risk/return as green +
    for i, f_ret in enumerate(na_avgrets):
        plt.plot(na_std[i], f_ret, 'g+')

    # # Plot some arrows showing transistion of efficient frontier
    # for i in range(0, 101, 10):
    #     plt.arrow(lf_std[i], lf_returns[i], lf_std_port_test[i] - lf_std[i],
    #                 lf_ret_port_test[i] - lf_returns[i], color='k')

    # Labels and Axis
    plt.legend(['2009 Frontier', '2010 Frontier',
        'Performance of \'09 Frontier in 2010'], loc='lower right')
    plt.title('Efficient Frontier For S&P 100 ')
    plt.ylabel('Expected Return')
    plt.xlabel('StDev')
    plt.savefig('tutorial8.pdf', format='pdf')

if __name__ == '__main__':
    main()
