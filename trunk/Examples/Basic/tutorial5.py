'''
(c) 2011, 2012 Lucena Research, LLC. All rights reserved.

Created on Jan 1, 2011

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
import cPickle
import datetime as dt


#qstk imports
from quicksim import quickSim as qs

#STRATegy to use
STRAT = os.environ['QS']+"/quicksim/STRATegies/OneStock.py"

#start and end dates to start from
start = dt.datetime(2008,  4, 1)
end = dt.datetime(2012,  4, 1)

#number of tests to do and the number of days offset
num = 10
offset = 1

#starting fund value
startval=10000

#perform tests
fundsmatrix = qs.strat_backtest1(STRAT,  start, end, 1, offset, startval)

#output fundsmatrix to pickle file
output=open(os.environ['QS']+'/Examples/Basic/temp_fundsmatrix.pkl',  "w")
cPickle.dump(fundsmatrix,  output)
output.close()

#graph tests using report
os.system('python '+os.environ['QS']+'/Bin/report.py '+os.environ['QS']+'/Examples/Basic/temp_fundsmatrix.pkl')
