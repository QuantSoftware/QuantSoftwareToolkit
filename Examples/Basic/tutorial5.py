'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on January, 24, 2013

@author: Sourabh Bajaj
@contact: sourabhbajaj@gatech.edu
@summary: Contains tutorial for backtester.
'''

# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import QSTK.qstktools.report as report
import QSTK.qstksim as qstksim

# Third Party Imports
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def main():
    '''Main Function'''

    # List of symbols
    ls_symbols = ["AAPL", "GOOG"]

    # Start and End date of the charts
    dt_start = dt.datetime(2008, 1, 1)
    dt_end = dt.datetime(2010, 12, 31)

    # We need closing prices so the timestamp should be hours=16.
    dt_timeofday = dt.timedelta(hours=16)

    # Get a list of trading days between the start and the end.
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)

    # Creating an object of the dataaccess class with Yahoo as the source.
    c_dataobj = da.DataAccess('Yahoo')

    # Reading just the close prices
    df_close = c_dataobj.get_data(ldt_timestamps, ls_symbols, "close")

    # Creating the allocation dataframe
    # We offset the time for the simulator to have atleast one
    # datavalue before the allocation.
    df_alloc = pd.DataFrame(np.array([[0.5, 0.5]]),
                index=[ldt_timestamps[0] + dt.timedelta(hours=5)],
                columns=ls_symbols)

    dt_last_date = ldt_timestamps[0]
    # Looping through all dates and creating monthly allocations
    for dt_date in ldt_timestamps[1:]:
        if dt_last_date.month != dt_date.month:
            # Create allocation
            na_vals = np.random.randint(0, 1000, len(ls_symbols))
            na_vals = na_vals / float(sum(na_vals))
            na_vals = na_vals.reshape(1, -1)
            # Append to the dataframe
            df_new_row = pd.DataFrame(na_vals, index=[dt_date],
                                        columns=ls_symbols)
            df_alloc = df_alloc.append(df_new_row)
        dt_last_date = dt_date

    # Adding cash to the allocation matrix
    df_alloc['_CASH'] = 0.0

    # Running the simulator on the allocation frame
    (ts_funds, ts_leverage, f_commission, f_slippage, f_borrow_cost) = qstksim.tradesim(df_alloc,
                    df_close, f_start_cash=10000.0, i_leastcount=1, b_followleastcount=True,
                    f_slippage=0.0005, f_minimumcommision=5.0, f_commision_share=0.0035,
                    i_target_leverage=1, f_rate_borrow=3.5, log="transaction.csv")

    print "Simulated Fund Time Series : "
    print ts_funds
    print "Transaction Costs : "
    print "Commissions : ", f_commission
    print "Slippage : ", f_slippage
    print "Borrowing Cost : ", f_borrow_cost

if __name__ == '__main__':
    main()
