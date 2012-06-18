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


# Python imports
import os
import cPickle
import sys
import datetime as dt

# 3rd Party Imports
import numpy.core.multiarray
import pandas as pand

# QSTK imports
import qstksim as qs
from qstkutil import qsdateutil as du
from qstkutil import DataAccess as da


def quickSim( alloc, historic, start_cash ):
    """
    @summary Quickly back tests an allocation for certain historical data, 
             using a starting fund value
    @param alloc: DataMatrix containing timestamps to test as indices and 
                 Symbols to test as columns, with _CASH symbol as the last 
                 column
    @param historic: Historic dataframe of equity prices
    @param start_cash: integer specifing initial fund value
    @return funds: TimeSeries with fund values for each day in the back test
    @rtype TimeSeries
    """
    
    from inspect import currentframe, getframeinfo
    frameinfo = getframeinfo(currentframe())
    raise DeprecationWarning('Please use qstksim.tradesim instead, or' +
                              ' comment me out in %s, line %i'%(frameinfo.filename, 
                                                              frameinfo.lineno))
    
    #original quick simulator
    #not designed to handle shorts
    
    #check each row in alloc
    for row in range( 0, len(alloc.values[:, 0]) ):
        if( abs(alloc.values[row, :].sum() - 1) > .0001 ):
            print "warning, alloc row " + str(row) + \
            "does not sum to one, rebalancing"
            #if no allocation, all in cash
            if(alloc.values[row, :].sum()==0):
                alloc.values[row, -1] = 1
            else:
                alloc.values[row, :] = alloc.values[row, :]  \
                / alloc.values[row, :].sum()
    
    # add cash column
    historic['_CASH'] = 1



    closest = historic[historic.index <= alloc.index[0]].ix[:]


    # start shares/fund out as 100% cash
    fund_ts = pand.Series( [start_cash], index = [closest.index[0]] )
    
    shares = (alloc.ix[0:1] * 0.0)
    shares['_CASH'] = start_cash
    
    #compute all trades in the allocation frame
    for row_index, row in alloc.iterrows():
        
        trade_price = historic.ix[row_index:].ix[0:1]
        trade_date = trade_price.index[0]
        
        # get stock prices on all the days up until this trade
        to_calculate = historic[ (historic.index <= trade_date) &
                                 (historic.index > fund_ts.index[-1]) ]
        
        # multiply prices by our current shares
        values_by_stock = to_calculate * shares.ix[-1]
        
        # calculate total value and append to our fund history
        fund_ts = fund_ts.append( values_by_stock.sum(axis=1) )

        # Get new shares values
        shares = (row * fund_ts.ix[-1]) / trade_price

    return fund_ts

def _compute_short(arr):
    ''' Computes total value of negative positions '''
    tally = 0
    for i in range(0, len(arr) - 1):
        if arr[i] < 0:
            tally = tally+arr[i]
    return abs(tally)

def _compute_long(arr):
    ''' Computes total value of positive positions '''
    tally = 0
    for i in range(0, len(arr) - 1):
        if arr[i] > 0:
            tally = tally+arr[i]
    return tally
    
def _compute_leverage(arr, fundval):
    ''' Computes percent leverage '''
    if fundval == 0:
        return 0
    return (_compute_long(arr) - _compute_short(arr))/fundval
    
def shortingQuickSim(alloc, historic, start_cash, leverage):
    ''' shortingQuickSim
        designed to handle shorts, keeps track of leverage keeping it within
        paramaterized value, ignore alloc cash column '''

    del alloc['_CASH']
    #fix invalid days
    historic = historic.fillna(method='backfill') 
    
    #compute first trade
    closest = historic[historic.index <= alloc.index[0]]
    fund_ts = pand.Series( [start_cash], index = [closest.index[-1]] )
    shares = alloc.values[0, :] * fund_ts.values[-1] / closest.values[-1, :]
    cash_values = pand.DataMatrix( [shares * closest.values[-1, :]], 
                                   index=[closest.index[-1]] )
    
    #compute all trades
    for i in range(1, len(alloc.values[:, 0])):
        #check leverage
        #TODO Find out what to use for fundvall below...
        this_leverage = _compute_leverage( alloc.values[0, :], start_cash )
        if this_leverage > leverage:
            print 'Warning, leverage of ', this_leverage, \
                  ' reached, exceeds leverage limit of ', leverage, '\n'
        #get closest date(previous date)
        closest = historic[ historic.index <= alloc.index[i] ]
        #for loop to calculate fund daily (without rebalancing)
        for date in closest[ closest.index > fund_ts.index[-1] ].index:
            #compute and record total fund value (Sum(closest close * stocks))
            fund_ts = fund_ts.append( pand.Series(
                      [(closest.xs(date) * shares).sum()], index=[date]) )
            cash_values = cash_values.append( pand.DataMatrix(
                                   [shares*closest.xs(date)], index=[date]) )
        
        #distribute fund in accordance with alloc
        shares = alloc.values[i, :] * (
                 fund_ts.values[-1] / closest.xs(closest.index[-1]) )

    #compute fund value for rest of historic data with final share distribution
    for date in historic[ historic.index > alloc.index[-1] ].index:
        if date in closest.index:
            fund_ts = fund_ts.append( 
                      pand.Series( [(closest.xs(date) * shares).sum()], 
                                   index=[date]) )  

    #return fund record
    return fund_ts

def alloc_backtest(alloc, start):
    """
    @summary: Back tests an allocation from a pickle file. Uses a starting 
              portfolio value of start.
    @param alloc: Name of allocation pickle file. Pickle file contains a 
                  DataMatrix with timestamps as indexes and stock symbols as
                  columns, with the last column being the _CASH symbol, 
                  indicating how much
    of the allocation is in cash.
    @param start: integer specifying the starting value of the portfolio
    @return funds: List of fund values indicating the value of the portfolio 
                   throughout the back test.
    @rtype timeSeries
    """
    
    #read in alloc table from command line arguements
    alloc_input_file = open(alloc, "r")
    alloc = cPickle.load(alloc_input_file)
    
    # Get the data from the data store
    dataobj = da.DataAccess('Norgate')
    startday=alloc.index[0]-dt.timedelta(days=10)
    endday = alloc.index[-1]

    # Get desired timestamps
    timeofday=dt.timedelta(hours=16)
    timestamps = du.getNYSEdays(startday,endday,timeofday)
    historic = dataobj.get_data( timestamps, list(alloc.columns[0:-1]),
                                 "close" )
    #backtestx
    [fund, leverage, commissions, slippage]= qs.tradesim(alloc, historic, int(start), 1, True, 0.02, 5, 0.02 )

    return [fund, leverage, commissions, slippage]

def strat_backtest1(strat, start, end, num, diff, startval):
    """
    @summary: Back tests a strategy defined in a python script that takes
              in a start
    and end date along with a starting value a set number of times. 
    @param strat: filename of python script strategy
    @param start: starting date in a datetime object
    @param end: ending date in a datetime object
    @param num: number of tests to perform
    @param diff: offset in days of the tests
    @param startval: starting value of fund during back tests
    @return fundsmatrix: Datamatrix of fund values returned from each test
    @rtype datamatrix
    """
    fundsmatrix = []
    startdates = du.getNextNNYSEdays(start, num * diff, dt.timedelta(hours=16))
    enddates = du.getNextNNYSEdays(end, num * diff, dt.timedelta(hours=16))
    for i in range(0, num):
        os.system( 'python ' + strat + ' ' + startdates[i].strftime("%m-%d-%Y")\
                    + ' ' + enddates[i].strftime("%m-%d-%Y") + \
                    ' temp_alloc.pkl')
        
        return alloc_backtest('temp_alloc.pkl', startval)
    return fundsmatrix
    
def strat_backtest2(strat, start, end, diff, dur, startval):
    """
    @summary: Back tests a strategy defined in a python script that takes in a
             start and end date along with a starting value over a given 
             period.
    @param strat: filename of python script strategy
    @param start: starting date in a datetime object
    @param end: ending date in a datetime object
    @param diff: offset in days of the tests
    @param dur: length of a test
    @param startval: starting value of fund during back tests
    @return fundsmatrix: Datamatrix of fund values returned from each test
    @rtype datamatrix
    """
    fundsmatrix = []
    startdates = du.getNYSEdays( start, end, dt.timedelta(hours=16) )
    for i in range(0, len(startdates), diff):
        if( i + dur>=len(startdates) ):
            enddate = startdates[-1]
        else:
            enddate = startdates[i+dur]
        os.system('python ' + strat + ' ' + startdates[i].strftime("%m-%d-%Y")\
                   + ' ' + enddate.strftime("%m-%d-%Y") + ' temp_alloc.pkl')
        funds = alloc_backtest('temp_alloc.pkl', startval)
        fundsmatrix.append(funds)
    return fundsmatrix

def run_main():
    ''' Main program '''
    
    #
    # CmdlnQuickSim
    #
    # A function which runs a quick sim on an allocation provided via 
    # command line,
    # along with a starting cash value
    # 
    # Allocation Backtest:
    # python quickSim.py -a allocation_fiel start_value output_file
    # python quickSim.py -a 'alloc_file.pkl' 1000 'fund_output.pkl'
    #
    # Strategy backtest:
    # python quickSim.py -s strategy start end start_value output_file
    # python quickSim.py -s 'strategy.py' '2/2/2007' '2/2/2009' 1000 
    # 'fund_output.pkl' 
    #
    # Robust backtest:
    # python quickSim.py -r strategy start end days_between duration
    # start_value output
    # python quickSim.py -r 'strategy.py' '1-1-2004' '1-1-2007' 7 28 10000
    # 'out.pkl'
    # Drew Bratcher
    #

    if(sys.argv[1] == '-a'):
        funds = alloc_backtest(sys.argv[2], sys.argv[3])
        output = open(sys.argv[4], "w")
        cPickle.dump(funds, output)
    elif(sys.argv[1] == '-s'):
        t = map(int,  sys.argv[3].split('-'))
        startday = dt.datetime(t[2], t[0], t[1])
        t = map(int,  sys.argv[4].split('-'))
        endday = dt.datetime(t[2], t[0], t[1])  
        fundsmatrix = strat_backtest1(sys.argv[2], startday, endday, 1, 0, 
                                    int(sys.argv[5]))
        output = open(sys.argv[6], "w")
        cPickle.dump(fundsmatrix, output) 
    elif(sys.argv[1] == '-r'):
        t = map(int, sys.argv[3].split('-'))
        startday = dt.datetime(t[2], t[0], t[1])
        t = map(int, sys.argv[4].split('-'))
        endday = dt.datetime(t[2], t[0], t[1])
        fundsmatrix = strat_backtest2(sys.argv[2], startday, endday,
                                    int(sys.argv[5]), int(sys.argv[6]),
                                    int(sys.argv[7]))
        output = open(sys.argv[8], "w")
        cPickle.dump(fundsmatrix, output)
    else:
        print 'invalid command line call'
        print 'use python quickSim.py -a alloc_pkl start_value output_pkl'
        print 'or python quickSim.py -s strategy start_date end_date' + \
              'start_value output_pkl'
        print 'or python quickSim.py -r strategy start_date end_date' + \
              ' test_offset_in_days duration start_value output_pkl'

if __name__ == "__main__":
    run_main()
