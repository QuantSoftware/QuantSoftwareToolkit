'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on October, 4, 2013

@author: Sourabh Bajaj
@contact: sourabhbajaj@gatech.edu
@summary: Example tutorial code.
'''

import pandas as pd
import datetime as dt
import numpy as np

## Tutorial on using Pandas in QSTK
ldt_timestamps = []
for i in range(1, 6):
    ldt_timestamps.append(dt.datetime(2011, 1, i, 16))

print "The index we created has the following dates : "
print ldt_timestamps
print

## TimeSeries
ts_single_value = pd.TimeSeries(0.0, index=ldt_timestamps)
print "A timeseries initialized to one single value : "

na_vals = np.arange(len(ldt_timestamps))
print "Dummy initialized array : "
print na_vals
print

ts_array = pd.TimeSeries(na_vals, index=ldt_timestamps)
print "A timeseries initialized using a numpy array : "
print ts_array
print 

print "Reading the timeseries for a particular date"
print "Date :  ", ldt_timestamps[1]
print "Value : ", ts_array[ldt_timestamps[1]]
print

print "Initializing a list of symbols : "
ls_symbols = ['AAPL', 'GOOG', 'MSFT', 'IBM']
print ls_symbols
print

print "Initializing a dataframe with one value : "
df_single = pd.DataFrame(index=ldt_timestamps, columns=ls_symbols)
df_single = df_single.fillna(0.0)
print df_single
print

print "Initializing a dataframe with a numpy array : "
na_vals_2 = np.random.randn(len(ldt_timestamps), len(ls_symbols))
df_vals = pd.DataFrame(na_vals_2, index=ldt_timestamps, columns=ls_symbols)
print df_vals
print 

print "Access the timeseries of a particular symbol : "
print df_vals[ls_symbols[1]]
print

print "Access the timeseries of a particular date : "
print df_vals.ix[ldt_timestamps[1]]
print

print "Access the value for a specific symbol on a specific date: "
print df_vals[ls_symbols[1]].ix[ldt_timestamps[1]]
print

print "Reindexing the dataframe"
ldt_new_dates = [dt.datetime(2011, 1, 3, 16), 
                 dt.datetime(2011, 1, 5, 16),
                 dt.datetime(2011, 1, 7, 16)]
ls_new_symbols = ['AAPL', 'IBM', 'XOM']
df_new = df_vals.reindex(index=ldt_new_dates, columns=ls_new_symbols)
print df_new
print "Observe that reindex carried over whatever values it could find and set the rest to NAN"
print

print "For pandas rolling statistics please refer : http://pandas.pydata.org/pandas-docs/dev/computation.html#moving-rolling-statistics-moments"

