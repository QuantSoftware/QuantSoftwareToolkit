'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.


Created on September, 12, 2011

@author:Drew Bratcher
@contact: dbratcher@gatech.edu
@summary: Contains tutorial for backtester and report.

'''


#
# tutorial5.py
#
# @summary: Uses the quicksim backtester and OneStock strategy to create
# and back test an allocation. Displays the result using the report module.
#
# @author: Drew Bratcher
#
#

#python imports
import os
import pandas as pand
import datetime as dt

#qstk imports
import qstksim
import qstkutil.DataAccess as da
import qstkutil.qsdateutil as du
from Bin import report
        
startday = dt.datetime(2008, 1, 1)
endday = dt.datetime(2011, 2, 1)

l_symbols = ['AAPL']

#Get desired timestamps
timeofday = dt.timedelta(hours = 16)
ldt_timestamps = du.getNYSEdays(startday, endday, timeofday)

dataobj = da.DataAccess('Norgate')
df_close = dataobj.get_data( \
                ldt_timestamps, l_symbols, "close", verbose=True)

df_alloc = pand.DataFrame(index=[dt.datetime(2009, 2, 1)], data=[1], columns=l_symbols)

for i in range(11):
    df_alloc = df_alloc.append( \
             pand.DataFrame(index=[dt.datetime(2009, i+2, 3)], \
                              data=[1], columns=l_symbols))

df_alloc['_CASH'] = 0.0

''' Tests tradesim buy-on-open functionality '''
(df_funds, ts_leverage, f_commision, f_slippage) = qstksim.tradesim( df_alloc, df_close, 10000, 1, True, 0.02, 5, 0.02)

df_goog = pand.DataFrame(index=df_funds.index, data=df_funds.values, columns=l_symbols)
print df_goog
report.print_stats(df_goog, ["$SPX"], "AAPL", leverage=ts_leverage, commissions=f_commision, slippage=f_slippage, directory="./AAPL/")