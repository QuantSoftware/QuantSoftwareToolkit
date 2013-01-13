'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on Jan 1, 2011

@author:Drew Bratcher
@contact: dbratcher@gatech.edu
@summary: Contains tutorial for backtester and report.

'''


# OneStock.py
#
# Usage: python OneStock.py '1-1-2004' '1-1-2009' 'alloc.pkl'
#
# A strategy script which creates a daily allocation table using one stock (GOOG)
# and the start and end dates provided by the user.
# It then dumps the allocation table to a pickle file.
#
#

# python imports
import cPickle
import sys
from pandas import DataMatrix
import datetime as dt
import random

# qstk imports
import qstkutil.DataAccess as da
import qstkutil.qsdateutil as du

if __name__ == "__main__":
    print "Running One Stock strategy from "+sys.argv[1] +" to "+sys.argv[2]

    # Use google symbol
    symbols = list(['SPY'])

    # Set start and end dates
    t = map(int,sys.argv[1].split('-'))
    startday = dt.datetime(t[2],t[0],t[1])
    t = map(int,sys.argv[2].split('-'))
    endday = dt.datetime(t[2],t[0],t[1])

    # Get desired timestamps
    timeofday=dt.timedelta(hours=16)
    timestamps = du.getNYSEdays(startday,endday,timeofday)

    # Get the data from the data store
    dataobj = da.DataAccess('Norgate')
    historic = dataobj.get_data(timestamps, symbols, "close")

    # Setup the allocation table
    alloc_val= random.random()
    alloc=DataMatrix(index=[historic.index[0]], data=[alloc_val], columns=symbols)
    for date in range(1, len(historic.index)):
        alloc_val=1 #random.random()
        alloc=alloc.append(DataMatrix(index=[historic.index[date]], data=[alloc_val], columns=[symbols[0]]))
    alloc['_CASH']=1-alloc[symbols[0]]

    # Dump to pkl file
    output=open(sys.argv[3],"wb")
    cPickle.dump(alloc, output)
