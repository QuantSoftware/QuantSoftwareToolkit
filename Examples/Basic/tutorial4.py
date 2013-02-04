'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on January, 24, 2013

@author: Sourabh Bajaj
@contact: sourabhbajaj@gatech.edu
@summary: Example tutorial code.
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
import cPickle


def main():
    ''' Main Function'''

    # Start and End date of the charts
    dt_start = dt.datetime(2004, 1, 1)
    dt_end = dt.datetime(2009, 12, 31)

    # We need closing prices so the timestamp should be hours=16.
    dt_timeofday = dt.timedelta(hours=16)

    # Get a list of trading days between the start and the end.
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)

    # Creating an object of the dataaccess class with Yahoo as the source.
    c_dataobj = da.DataAccess('Yahoo')

    # List of symbols - First 20
    ls_symbols = c_dataobj.get_symbols_from_list('sp5002012')
    ls_symbols = ls_symbols[:20]
    ls_symbols.append('_CASH')

    # Creating the first allocation row
    na_vals = np.random.randint(0, 1000, len(ls_symbols))
    # Normalize the row - Typecasting as everything is int.
    na_vals = na_vals / float(sum(na_vals))
    # Reshape to a 2D matrix to append into dataframe.
    na_vals = na_vals.reshape(1, -1)

    # Creating Allocation DataFrames
    df_alloc = pd.DataFrame(na_vals, index=[ldt_timestamps[0]],
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

    # Create the outpul pickle file for the dataframe.
    output = open('allocation.pkl', 'wb')
    cPickle.dump(df_alloc, output)

if __name__ == '__main__':
    main()
