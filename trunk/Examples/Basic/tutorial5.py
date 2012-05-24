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
import datetime as dt

#qstk imports
from quicksim import quickSim as qs
from Bin import report

#STRATegy to use
STRAT = os.environ['QS']+"/quicksim/STRATegies/OneStock.py"

#start and end dates to start from
START = dt.datetime(2009,  5, 1)
END = dt.datetime(2009,  9, 1)

#number of tests to do and the number of days offset
NUM = 10
OFFSET = 1

#starting fund value
STARTVAL = 10000

#perform tests

FUNDS = qs.strat_backtest1(STRAT, START, END, 1, OFFSET, STARTVAL)

report.print_stats(FUNDS[0], ["$SPX"], "FUND TITLE")
report.print_plot(FUNDS, ["$SPX"], "FUND TITLE", "FundFile.png")
