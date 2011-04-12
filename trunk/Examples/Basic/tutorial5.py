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
from pandas import *

#qstk imports
from quicksim import quickSim as qs

#strategy to use
strat = os.environ['QS']+"/quicksim/strategies/OneStock.py"

#start and end dates to start from
start = dt.datetime(2004,1,1)
end = dt.datetime(2009,1,1)

#number of tests to do and the number of days offset
num = 10
offset = 1

#starting fund value
startval=1000

#perform tests
fundsmatrix = qs.strat_backtest(strat,start,end,1,offset,startval)

#output fundsmatrix to pickle file
output=open(os.environ['QS']+'/Examples/Basic/temp_fundsmatrix.pkl',"w")
cPickle.dump(fundsmatrix,output)
output.close()

#graph tests using report
os.system('python '+os.environ['QS']+'/Bin/report.py '+os.environ['QS']+'/Examples/Basic/temp_fundsmatrix.pkl')
