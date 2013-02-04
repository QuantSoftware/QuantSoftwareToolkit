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
    df_alloc = pd.DataFrame(np.array([[0.5, 0.5]]), index=[ldt_timestamps[0]],
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
                    df_close, 10000.0, 1, True, 0.0005, 5.0, 0.0035, 1, 3.5, log="transaction.csv")

if __name__ == '__main__':
    main()


# #python imports
# import os
# import pandas as pand
# import datetime as dt
# import random as rgen

# #qstk imports
# import QSTK.qstksim
# import QSTK.qstkutil.DataAccess as da
# import QSTK.qstkutil.qsdateutil as du
# import QSTK.qstktools.report as report
# import QSTK.qstktools.csv2fund as csv2fund

# startday = dt.datetime(2008, 1, 1)
# endday = dt.datetime(2012, 2, 1)

# l_symbols = ['AAPL','GOOG']

# #Get desired timestamps
# timeofday = dt.timedelta(hours = 16)
# ldt_timestamps = du.getNYSEdays(startday, endday, timeofday)

# dataobj = da.DataAccess('Yahoo')
# df_close = dataobj.get_data( \
#                 ldt_timestamps, l_symbols, "close", verbose=False)

# df_alloc = pand.DataFrame(index=[dt.datetime(2008, 2, 1)], data=[[0.5,0.5]], columns=l_symbols)

# for day in ldt_timestamps:
#     randomfloat=rgen.random()
#     df_alloc = df_alloc.append( \
#              pand.DataFrame(index=[day], \
#                               data=[[randomfloat, 1-randomfloat]], columns=l_symbols))
    

# df_alloc['_CASH'] = 0

# ''' Tests tradesim buy-on-open functionality '''
# (df_funds, ts_leverage, f_commision, f_slippage) = qstksim.tradesim( df_alloc, df_close, 1000000, 1, True, 0.02, 5, 0.02, log="transactions.csv")
# df_aapl = pand.DataFrame(index=df_funds.index, data=df_funds.values, columns=["FUND"])
# l_symbols = ['GOOG','MSFT']

# #Get desired timestamps
# timeofday = dt.timedelta(hours = 16)
# ldt_timestamps = du.getNYSEdays(startday, endday, timeofday)

# dataobj = da.DataAccess('Yahoo')
# df_close = dataobj.get_data( \
#                 ldt_timestamps, l_symbols, "close", verbose=False)

# df_alloc = pand.DataFrame(index=[dt.datetime(2008, 2, 1)], data=[[0.5,0.5]], columns=l_symbols)

# for day in ldt_timestamps:
#     randomfloat=rgen.random()
#     df_alloc = df_alloc.append( \
#              pand.DataFrame(index=[day], \
#                               data=[[randomfloat, 1-randomfloat]], columns=l_symbols))
    

# df_alloc['_CASH'] = 0

# ''' Tests tradesim buy-on-open functionality '''
# (df_funds, ts_leverage, f_commision, f_slippage) = qstksim.tradesim( df_alloc, df_close, 1000000, 1, True, 0.02, 5, 0.02, log="transactions2.csv")
# df_goog = pand.DataFrame(index=df_funds.index, data=df_funds.values, columns=["FUND"])

# report.print_stats(df_aapl, ["$SPX","MSFT"], "AAPL", s_fund_name="Test Portfolio", original=df_goog, s_original_name="UnHedged", d_trading_params={"Number of trades":200,"Trading Period":"Weekly"} s_comments="This is a sample report generated by tutorial 5.", commissions=f_commision, slippage=f_slippage, directory="./AAPL/")
# #print "Analyzing Transactions..."
# #csv2fund.analyze_transactions("transactions.csv","AAPL")
# print "Done"
