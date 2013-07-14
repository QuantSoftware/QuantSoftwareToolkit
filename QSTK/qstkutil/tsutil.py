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


import math
import datetime as dt
import numpy as np
from QSTK.qstkutil import qsdateutil
from math import sqrt
import pandas as pd
from copy import deepcopy


import random as rand

from QSTK.qstkutil import DataAccess as da
from QSTK.qstkutil import qsdateutil as du
import numpy as np

def daily(lfFunds):
    """
    @summary Computes daily returns centered around 0
    @param funds: A time series containing daily fund values
    @return an array of daily returns
    """
    if type(lfFunds) == type(pd.Series()):
        ldt_timestamps = du.getNYSEdays(lfFunds.index[0], lfFunds.index[-1], dt.timedelta(hours=16))
        lfFunds = lfFunds.reindex(index=ldt_timestamps, method='ffill')
    nds = np.asarray(deepcopy(lfFunds))
    s= np.shape(nds)
    if len(s)==1:
        nds=np.expand_dims(nds,1)
    returnize0(nds)
    return(nds)

def daily1(lfFunds):
    """
    @summary Computes daily returns centered around 1
    @param funds: A time series containing daily fund values
    @return an array of daily returns
    """
    nds = np.asarray(deepcopy(lfFunds))
    s= np.shape(nds)
    if len(s)==1:
        nds=np.expand_dims(nds,1)
    returnize1(nds)
    return(nds)

def monthly(funds):
    """
    @summary Computes monthly returns centered around 0
    @param funds: A time series containing daily fund values
    @return an array of monthly returns
    """
    funds2 = []
    last_last_month = -1
    years = qsdateutil.getYears(funds)
    for year in years:
        months = qsdateutil.getMonths(funds, year)
        for month in months:
            last_this_month = qsdateutil.getLastDay(funds, year, month)
            if last_last_month == -1 :
                last_last_month=qsdateutil.getFirstDay(funds, year, month)
            if type(funds).__name__=='TimeSeries':
                funds2.append(funds[last_this_month]/funds[last_last_month]-1)
            else:
                funds2.append(funds.xs(last_this_month)/funds.xs(last_last_month)-1)
            last_last_month = last_this_month
    return(funds2)

def average_monthly(funds):
    """
    @summary Computes average monthly returns centered around 0
    @param funds: A time series containing daily fund values
    @return an array of average monthly returns
    """
    rets = daily(funds)
    ret_i = 0
    years = qsdateutil.getYears(funds)
    averages = []
    for year in years:
        months = qsdateutil.getMonths(funds, year)
        for month in months:
            avg = 0
            count = 0
            days = qsdateutil.getDays(funds, year, month)
            for day in days:
                avg += rets[ret_i]
                ret_i += 1
                count += 1
            averages.append(float(avg) / count)
    return(averages)    

def fillforward(nds):
    """
    @summary Removes NaNs from a 2D array by scanning forward in the 
    1st dimension.  If a cell is NaN, the value above it is carried forward.
    @param nds: the array to fill forward
    @return the array is revised in place
    """
    for col in range(nds.shape[1]):
        for row in range(1, nds.shape[0]):
            if math.isnan(nds[row, col]):
                nds[row, col] = nds[row-1, col]

def fillbackward(nds):
    """
    @summary Removes NaNs from a 2D array by scanning backward in the 
    1st dimension.  If a cell is NaN, the value above it is carried backward.
    @param nds: the array to fill backward
    @return the array is revised in place
    """
    for col in range(nds.shape[1]):
        for row in range(nds.shape[0] - 2, -1, -1):
            if math.isnan(nds[row, col]):
                nds[row, col] = nds[row+1, col]


def returnize0(nds):
    """
    @summary Computes stepwise (usually daily) returns relative to 0, where
    0 implies no change in value.
    @return the array is revised in place
    """
    if type(nds) == type(pd.DataFrame()):
        nds = (nds / nds.shift(1)) - 1.0
        nds = nds.fillna(0.0)
        return nds

    s= np.shape(nds)
    if len(s)==1:
        nds=np.expand_dims(nds,1)
    nds[1:, :] = (nds[1:, :] / nds[0:-1]) - 1
    nds[0, :] = np.zeros(nds.shape[1])
    return nds


def returnize1(nds):
    """
    @summary Computes stepwise (usually daily) returns relative to 1, where
    1 implies no change in value.
    @param nds: the array to fill backward
    @return the array is revised in place
    """
    if type(nds) == type(pd.DataFrame()):
        nds = nds / nds.shift(1)
        nds = nds.fillna(1.0)
        return nds

    s= np.shape(nds)
    if len(s)==1:
        nds=np.expand_dims(nds,1)
    nds[1:, :] = (nds[1:, :]/nds[0:-1])
    nds[0, :] = np.ones(nds.shape[1])
    return nds


def priceize1(nds):
    """
    @summary Computes stepwise (usually daily) returns relative to 1, where
    1 implies no change in value.
    @param nds: the array to fill backward
    @return the array is revised in place
    """
    
    nds[0, :] = 100 
    for i in range(1, nds.shape[0]):
        nds[i, :] = nds[i-1, :] * nds[i, :]
    
    
def logreturnize(nds):
    """
    @summary Computes stepwise (usually daily) logarithmic returns.
    @param nds: the array to fill backward
    @return the array is revised in place
    """
    returnize1(nds)
    nds = np.log(nds)
    return nds

def get_winning_days( rets):
    """
    @summary Returns the percentage of winning days of the returns.
    @param rets: 1d numpy array or fund list of daily returns (centered on 0)
    @return Percentage of winning days
    """
    negative_rets = []
    for i in rets:
        if(i<0):
            negative_rets.append(i)
    return 100 * (1 - float(len(negative_rets)) / float(len(rets)))

def get_max_draw_down(ts_vals):
    """
    @summary Returns the max draw down of the returns.
    @param ts_vals: 1d numpy array or fund list
    @return Max draw down
    """
    MDD = 0
    DD = 0
    peak = -99999
    for value in ts_vals:
        if (value > peak):
            peak = value
        else:
            DD = (peak - value) / peak
        if (DD > MDD):
            MDD = DD
    return -1*MDD

def get_sortino_ratio( rets, risk_free=0.00 ):
    """
    @summary Returns the daily Sortino ratio of the returns.
    @param rets: 1d numpy array or fund list of daily returns (centered on 0)
    @param risk_free: risk free return, default is 0%
    @return Sortino Ratio, computed off daily returns
    """
    rets = np.asarray(rets)
    f_mean = np.mean( rets, axis=0 )
    negative_rets = rets[rets < 0]
    f_dev = np.std( negative_rets, axis=0 )
    f_sortino = (f_mean*252 - risk_free) / (f_dev * np.sqrt(252))
    return f_sortino

def get_sharpe_ratio( rets, risk_free=0.00 ):
    """
    @summary Returns the daily Sharpe ratio of the returns.
    @param rets: 1d numpy array or fund list of daily returns (centered on 0)
    @param risk_free: risk free returns, default is 0%
    @return Annualized rate of return, not converted to percent
    """
    f_dev = np.std( rets, axis=0 )
    f_mean = np.mean( rets, axis=0 )
    
    f_sharpe = (f_mean *252 - risk_free) / ( f_dev * np.sqrt(252) )
    
    return f_sharpe

def get_ror_annual( rets ):
    """
    @summary Returns the rate of return annualized.  Assumes len(rets) is number of days.
    @param rets: 1d numpy array or list of daily returns
    @return Annualized rate of return, not converted to percent
    """

    f_inv = 1.0
    for f_ret in rets:
        f_inv = f_inv * f_ret
    
    f_ror_ytd = f_inv - 1.0    
    
    #print ' RorYTD =', f_inv, 'Over days:', len(rets)
    
    return ( (1.0 + f_ror_ytd)**( 1.0/(len(rets)/252.0) ) ) - 1.0

def getPeriodicRets( dmPrice, sOffset ):
    """
    @summary Reindexes a DataMatrix price array and returns the new periodic returns.
    @param dmPrice: DataMatrix of stock prices
    @param sOffset: Offset string to use, choose from _offsetMap in pandas/core/datetools.py
                    e.g. 'EOM', 'WEEKDAY', 'W@FRI', 'A@JAN'.  Or use a pandas DateOffset.
    """    
    
    # Could possibly use DataMatrix.asfreq here """
    # Use pandas DateRange to create the dates we want, use 4:00 """
    drNewRange = DateRange(dmPrice.index[0], dmPrice.index[-1], timeRule=sOffset)
    drNewRange += DateOffset(hours=16)
    
    dmPrice = dmPrice.reindex( drNewRange, method='ffill' )  

    returnize1( dmPrice.values )
    
    # Do not leave return of 1.0 for first time period: not accurate """
    return dmPrice[1:]

def getReindexedRets( rets, l_period ):
    """
    @summary Reindexes returns using the cumulative product. E.g. if returns are 1.5 and 1.5, a period of 2 will
             produce a 2-day return of 2.25.  Note, these must be returns centered around 1.
    @param rets: Daily returns of the various stocks (using returnize1)
    @param l_period: New target period.
    @note: Note that this function does not track actual weeks or months, it only approximates with trading days.
           You can use 5 for week, or 21 for month, etc.
    """    
    naCumData = np.cumprod(rets, axis=0)

    lNewRows =(rets.shape[0]-1) / (l_period)
    # We compress data into height / l_period + 1 new rows """
    for i in range( lNewRows ):
        lCurInd = -1 - i*l_period
        # Just hold new data in same array"""
        # new return is cumprod on day x / cumprod on day x-l_period """
        start=naCumData[lCurInd - l_period, :]
        naCumData[-1 - i, :] = naCumData[lCurInd, :] / start 
        # Select new returns from end of cumulative array """
    
    return naCumData[-lNewRows:, ]

        
def getOptPort(rets, f_target, l_period=1, naLower=None, naUpper=None, lNagDebug=0):
    """
    @summary Returns the Markowitz optimum portfolio for a specific return.
    @param rets: Daily returns of the various stocks (using returnize1)
    @param f_target: Target return, i.e. 0.04 = 4% per period
    @param l_period: Period to compress the returns to, e.g. 7 = weekly
    @param naLower: List of floats which corresponds to lower portfolio% for each stock
    @param naUpper: List of floats which corresponds to upper portfolio% for each stock 
    @return tuple: (weights of portfolio, min possible return, max possible return)
    """
    
    # Attempt to import library """
    try:
        pass
        import nagint as nag
    except ImportError:
        print 'Could not import NAG library'
        print 'make sure nagint.so is in your python path'
        return ([], 0, 0)
    
    # Get number of stocks """
    lStocks = rets.shape[1]
    
    # If period != 1 we need to restructure the data """
    if( l_period != 1 ):
        rets = getReindexedRets( rets, l_period)
    
    # Calculate means and covariance """
    naAvgRets = np.average( rets, axis=0 )
    naCov = np.cov( rets, rowvar=False )
    
    # Special case for None == f_target"""
    # simply return average returns and cov """
    if( f_target is None ):
        return naAvgRets, np.std(rets, axis=0)
    
    # Calculate upper and lower limits of variables as well as constraints """
    if( naUpper is None ): 
        naUpper = np.ones( lStocks )  # max portfolio % is 1
    
    if( naLower is None ): 
        naLower = np.zeros( lStocks ) # min is 0, set negative for shorting
    # Two extra constraints for linear conditions"""
    # result = desired return, and sum of weights = 1 """
    naUpper = np.append( naUpper, [f_target, 1.0] )
    naLower = np.append( naLower, [f_target, 1.0] )
    
    # Initial estimate of portfolio """
    naInitial = np.array([1.0/lStocks]*lStocks)
    
    # Set up constraints matrix"""
    # composed of expected returns in row one, unity row in row two """
    naConstraints = np.vstack( (naAvgRets, np.ones(lStocks)) )

    # Get portfolio weights, last entry in array is actually variance """
    try:
        naReturn = nag.optPort( naConstraints, naLower, naUpper, \
                                      naCov, naInitial, lNagDebug )
    except RuntimeError:
        print 'NAG Runtime error with target: %.02lf'%(f_target)
        return ( naInitial, sqrt( naCov[0][0] ) )  
    #return semi-junk to not mess up the rest of the plot

    # Calculate stdev of entire portfolio to return"""
    # what NAG returns is slightly different """
    fPortDev = np.std( np.dot(rets, naReturn[0,0:-1]) )
    
    # Show difference between above stdev and sqrt NAG covariance"""
    # possibly not taking correlation into account """
    #print fPortDev / sqrt(naReturn[0, -1]) 

    # Return weights and stdDev of portfolio."""
    #  note again the last value of naReturn is NAG's reported variance """
    return (naReturn[0, 0:-1], fPortDev)


def OptPort( naData, fTarget, naLower=None, naUpper=None, naExpected=None, s_type = "long"):
    """
    @summary Returns the Markowitz optimum portfolio for a specific return.
    @param naData: Daily returns of the various stocks (using returnize1)
    @param fTarget: Target return, i.e. 0.04 = 4% per period
    @param lPeriod: Period to compress the returns to, e.g. 7 = weekly
    @param naLower: List of floats which corresponds to lower portfolio% for each stock
    @param naUpper: List of floats which corresponds to upper portfolio% for each stock 
    @return tuple: (weights of portfolio, min possible return, max possible return)
    """
    ''' Attempt to import library '''
    try:
        pass
        from cvxopt import matrix
        from cvxopt.blas import dot
        from cvxopt.solvers import qp, options

    except ImportError:
        print 'Could not import CVX library'
        raise
    
    ''' Get number of stocks '''
    length = naData.shape[1]
    b_error = False

    naLower = deepcopy(naLower)
    naUpper = deepcopy(naUpper)
    naExpected = deepcopy(naExpected)
    
    # Assuming AvgReturns as the expected returns if parameter is not specified
    if (naExpected==None):
        naExpected = np.average( naData, axis=0 )

    na_signs = np.sign(naExpected)
    indices,  = np.where(na_signs == 0)
    na_signs[indices] = 1
    if s_type == "long":
        na_signs = np.ones(len(na_signs))
    elif s_type == "short":
        na_signs = np.ones(len(na_signs))*(-1)
    
    naData = na_signs*naData
    naExpected = na_signs*naExpected

    # Covariance matrix of the Data Set
    naCov=np.cov(naData, rowvar=False)
    
    # If length is one, just return 100% single symbol
    if length == 1:
        return (list(na_signs), np.std(naData, axis=0)[0], False)
    if length == 0:
        return ([], [0], False)
    # If we have 0/1 "free" equity we can't optimize
    # We just use     limits since we are stuck with 0 degrees of freedom
    
    ''' Special case for None == fTarget, simply return average returns and cov '''
    if( fTarget is None ):
        return (naExpected, np.std(naData, axis=0), b_error)
    
    # Upper bound of the Weights of a equity, If not specified, assumed to be 1.
    if(naUpper is None):
        naUpper= np.ones(length)
    
    # Lower bound of the Weights of a equity, If not specified assumed to be 0 (No shorting case)
    if(naLower is None):
        naLower= np.zeros(length)

    if sum(naLower) == 1:
        fPortDev = np.std(np.dot(naData, naLower))
        return (naLower, fPortDev, False)

    if sum(naUpper) == 1:
        fPortDev = np.std(np.dot(naData, naUpper))
        return (naUpper, fPortDev, False)
    
    naFree = naUpper != naLower
    if naFree.sum() <= 1:
        lnaPortfolios = naUpper.copy()
        
        # If there is 1 free we need to modify it to make the total
        # Add up to 1
        if naFree.sum() == 1:
            f_rest = naUpper[~naFree].sum()
            lnaPortfolios[naFree] = 1.0 - f_rest
            
        lnaPortfolios = na_signs * lnaPortfolios
        fPortDev = np.std(np.dot(naData, lnaPortfolios))
        return (lnaPortfolios, fPortDev, False)

    # Double the covariance of the diagonal elements for calculating risk.
    for i in range(length):
        naCov[i][i]=2*naCov[i][i]

    # Note, returns are modified to all be long from here on out
    (fMin, fMax) = getRetRange(False, naLower, naUpper, naExpected, "long") 
    #print (fTarget, fMin, fMax)
    if fTarget<fMin or fTarget>fMax:
        print "Target not possible", fTarget, fMin, fMax
        b_error = True

    naLower = naLower*(-1)
 
    # Setting up the parameters for the CVXOPT Library, it takes inputs in Matrix format.
    '''
    The Risk minimization problem is a standard Quadratic Programming problem according to the Markowitz Theory.
    '''
    S=matrix(naCov)
    #pbar=matrix(naExpected)
    naLower.shape=(length,1)
    naUpper.shape=(length,1)
    naExpected.shape = (1,length)
    zeo=matrix(0.0,(length,1))
    I = np.eye(length)
    minusI=-1*I
    G=matrix(np.vstack((I, minusI)))
    h=matrix(np.vstack((naUpper, naLower)))
    ones=matrix(1.0,(1,length)) 
    A=matrix(np.vstack((naExpected, ones)))
    b=matrix([float(fTarget),1.0])

    # Optional Settings for CVXOPT
    options['show_progress'] = False
    options['abstol']=1e-25
    options['reltol']=1e-24
    options['feastol']=1e-25
    

    # Optimization Calls
    # Optimal Portfolio
    try:
            lnaPortfolios = qp(S, -zeo, G, h, A, b)['x']
    except:
        b_error = True

    if b_error == True:
        print "Optimization not Possible"
        na_port = naLower*-1
        if sum(na_port) < 1:
            if sum(naUpper) == 1:
                na_port = naUpper
            else:
                i=0
                while(sum(na_port)<1 and i<25):
                    naOrder = naUpper - na_port
                    i = i+1
                    indices = np.where(naOrder > 0)
                    na_port[indices]= na_port[indices] + (1-sum(na_port))/len(indices[0]) 
                    naOrder = naUpper - na_port
                    indices = np.where(naOrder < 0)
                    na_port[indices]= naUpper[indices]
            
        lnaPortfolios = matrix(na_port)

    lnaPortfolios = (na_signs.reshape(-1,1) * lnaPortfolios).reshape(-1)
    # Expected Return of the Portfolio
    # lfReturn = dot(pbar, lnaPortfolios)
    
    # Risk of the portfolio
    fPortDev = np.std(np.dot(naData, lnaPortfolios))
    return (lnaPortfolios, fPortDev, b_error)


def getRetRange( rets, naLower, naUpper, naExpected = "False", s_type = "long"):
    """
    @summary Returns the range of possible returns with upper and lower bounds on the portfolio participation
    @param rets: Expected returns
    @param naLower: List of lower percentages by stock
    @param naUpper: List of upper percentages by stock
    @return tuple containing (fMin, fMax)
    """    
    
    # Calculate theoretical minimum and maximum theoretical returns """
    fMin = 0
    fMax = 0

    rets = deepcopy(rets)
    
    if naExpected == "False":
        naExpected = np.average( rets, axis=0 )
        
    na_signs = np.sign(naExpected)
    indices,  = np.where(na_signs == 0)
    na_signs[indices] = 1
    if s_type == "long":
        na_signs = np.ones(len(na_signs))
    elif s_type == "short":
        na_signs = np.ones(len(na_signs))*(-1)
    
    rets = na_signs*rets
    naExpected = na_signs*naExpected

    naSortInd = naExpected.argsort()
    
    # First add the lower bounds on portfolio participation """ 
    for i, fRet in enumerate(naExpected):
        fMin = fMin + fRet*naLower[i]
        fMax = fMax + fRet*naLower[i]


    # Now calculate minimum returns"""
    # allocate the max possible in worst performing equities """
    # Subtract min since we have already counted it """
    naUpperAdd = naUpper - naLower
    fTotalPercent = np.sum(naLower[:])
    for i, lInd in enumerate(naSortInd):
        fRetAdd = naUpperAdd[lInd] * naExpected[lInd]
        fTotalPercent = fTotalPercent + naUpperAdd[lInd]
        fMin = fMin + fRetAdd
        # Check if this additional percent puts us over the limit """
        if fTotalPercent > 1.0:
            fMin = fMin - naExpected[lInd] * (fTotalPercent - 1.0)
            break
    
    # Repeat for max, just reverse the sort, i.e. high to low """
    naUpperAdd = naUpper - naLower
    fTotalPercent = np.sum(naLower[:])
    for i, lInd in enumerate(naSortInd[::-1]):
        fRetAdd = naUpperAdd[lInd] * naExpected[lInd]
        fTotalPercent = fTotalPercent + naUpperAdd[lInd]
        fMax = fMax + fRetAdd
        
        # Check if this additional percent puts us over the limit """
        if fTotalPercent > 1.0:
            fMax = fMax - naExpected[lInd] * (fTotalPercent - 1.0)
            break

    return (fMin, fMax)


def _create_dict(df_rets, lnaPortfolios):

    allocations = {}
    for i, sym in enumerate(df_rets.columns):
        allocations[sym] = lnaPortfolios[i]

    return allocations

def optimizePortfolio(df_rets, list_min, list_max, list_price_target, 
                      target_risk, direction="long"):
    
    naLower = np.array(list_min)
    naUpper = np.array(list_max)
    naExpected = np.array(list_price_target)      

    b_same_flag = np.all( naExpected == naExpected[0])
    if b_same_flag and (naExpected[0] == 0):
        naExpected = naExpected + 0.1
    if b_same_flag:
        na_randomness = np.ones(naExpected.shape)
        target_risk = 0
        for i in range(len(na_randomness)):
            if i%2 ==0:
                na_randomness[i] = -1
        naExpected = naExpected + naExpected*0.0000001*na_randomness

    (fMin, fMax) = getRetRange( df_rets.values, naLower, naUpper, 
                                naExpected, direction)
    
    # Try to avoid intractible endpoints due to rounding errors """
    fMin += abs(fMin) * 0.00000000001 
    fMax -= abs(fMax) * 0.00000000001
    
    if target_risk == 1:
        (naPortWeights, fPortDev, b_error) = OptPort( df_rets.values, fMax, naLower, naUpper, naExpected, direction)
        allocations = _create_dict(df_rets, naPortWeights)
        return {'allocations': allocations, 'std_dev': fPortDev, 'expected_return': fMax, 'error': b_error}

    fStep = (fMax - fMin) / 50.0

    lfReturn =  [fMin + x * fStep for x in range(51)]
    lfStd = []
    lnaPortfolios = []
    
    for fTarget in lfReturn: 
        (naWeights, fStd, b_error) = OptPort( df_rets.values, fTarget, naLower, naUpper, naExpected, direction)
        if b_error == False:
            lfStd.append(fStd)
            lnaPortfolios.append( naWeights )
        else:
            # Return error on ANY failed optimization
            allocations = _create_dict(df_rets, np.zeros(df_rets.shape[1]))
            return {'allocations': allocations, 'std_dev': 0.0, 
                    'expected_return': fMax, 'error': True}

    if len(lfStd) == 0:
        (naPortWeights, fPortDev, b_error) = OptPort( df_rets.values, fMax, naLower, naUpper, naExpected, direction)
        allocations = _create_dict(df_rets, naPortWeights)
        return {'allocations': allocations, 'std_dev': fPortDev, 'expected_return': fMax, 'error': True}

    f_return = lfReturn[lfStd.index(min(lfStd))]

    if target_risk == 0:
        naPortWeights=lnaPortfolios[lfStd.index(min(lfStd))]    
        allocations = _create_dict(df_rets, naPortWeights)
        return {'allocations': allocations, 'std_dev': min(lfStd), 'expected_return': f_return, 'error': False}

    # If target_risk = 0.5, then return the one with maximum sharpe
    if target_risk == 0.5:
        lf_return_new = np.array(lfReturn)
        lf_std_new = np.array(lfStd)
        lf_std_new = lf_std_new[lf_return_new >= f_return]
        lf_return_new = lf_return_new[lf_return_new >= f_return]
        na_sharpe = lf_return_new / lf_std_new

        i_index_max_sharpe, = np.where(na_sharpe == max(na_sharpe))
        i_index_max_sharpe = i_index_max_sharpe[0]
        fTarget = lf_return_new[i_index_max_sharpe]
        (naPortWeights, fPortDev, b_error) = OptPort(df_rets.values, fTarget, naLower, naUpper, naExpected, direction)
        allocations = _create_dict(df_rets, naPortWeights)
        return {'allocations': allocations, 'std_dev': fPortDev, 'expected_return': fTarget, 'error': b_error}

    # Otherwise try to hit custom target between 0-1 min-max return
    fTarget = f_return + ((fMax - f_return) * target_risk)

    (naPortWeights, fPortDev, b_error) = OptPort( df_rets.values, fTarget, naLower, naUpper, naExpected, direction)
    allocations = _create_dict(df_rets, naPortWeights)
    return {'allocations': allocations, 'std_dev': fPortDev, 'expected_return': fTarget, 'error': b_error}
    

def getFrontier( rets, lRes=100, fUpper=0.2, fLower=0.00):
    """
    @summary Generates an efficient frontier based on average returns.
    @param rets: Array of returns to use
    @param lRes: Resolution of the curve, default=100
    @param fUpper: Upper bound on portfolio percentage
    @param fLower: Lower bound on portfolio percentage
    @return tuple containing (lf_ret, lfStd, lnaPortfolios)
            lf_ret: List of returns provided by each point
            lfStd: list of standard deviations provided by each point
            lnaPortfolios: list of numpy arrays containing weights for each portfolio
    """    
    
    # Limit/enforce percent participation """
    naUpper = np.ones(rets.shape[1]) * fUpper
    naLower = np.ones(rets.shape[1]) * fLower
    
    (fMin, fMax) = getRetRange( rets, naLower, naUpper )
    
    # Try to avoid intractible endpoints due to rounding errors """
    fMin *= 1.0000001 
    fMax *= 0.9999999

    # Calculate target returns from min and max """
    lf_ret = []
    for i in range(lRes):
        lf_ret.append( (fMax - fMin) * i / (lRes - 1) + fMin )
    
    
    lfStd = []
    lnaPortfolios = []
    
    # Call the function lRes times for the given range, use 1 for period """
    for f_target in lf_ret: 
        (naWeights, fStd) = getOptPort( rets, f_target, 1, \
                               naUpper=naUpper, naLower=naLower )
        lfStd.append(fStd)
        lnaPortfolios.append( naWeights )
    
    # plot frontier """
    #plt.plot( lfStd, lf_ret )
    plt.plot( np.std( rets, axis=0 ), np.average( rets, axis=0 ), \
                                                  'g+', markersize=10 ) 
    #plt.show()"""
    
    return (lf_ret, lfStd, lnaPortfolios)

        
def stockFilter( dmPrice, dmVolume, fNonNan=0.95, fPriceVolume=100*1000 ):
    """
    @summary Returns the list of stocks filtered based on various criteria.
    @param dmPrice: DataMatrix of stock prices
    @param dmVolume: DataMatrix of stock volumes
    @param fNonNan: Optional non-nan percent, default is .95
    @param fPriceVolume: Optional price*volume, default is 100,000
    @return list of stocks which meet the criteria
    """
    
    lsRetStocks = list( dmPrice.columns )

    for sStock in dmPrice.columns:
        fValid = 0.0
        print sStock
        # loop through all dates """
        for dtDate in dmPrice.index:
            # Count null (nan/inf/etc) values """
            fPrice = dmPrice[sStock][dtDate]
            if( not isnull(fPrice) ):
                fValid = fValid + 1
                # else test price volume """
                fVol = dmVolume[sStock][dtDate]
                if( not isnull(fVol) and fVol * fPrice < fPriceVolume ):
                    lsRetStocks.remove( sStock )
                    break

        # Remove if too many nan values """
        if( fValid / len(dmPrice.index) < fNonNan and sStock in lsRetStocks ):
            lsRetStocks.remove( sStock )

    return lsRetStocks


def getRandPort( lNum, dtStart=None, dtEnd=None, lsStocks=None,\
 dmPrice=None, dmVolume=None, bFilter=True, fNonNan=0.95,\
 fPriceVolume=100*1000, lSeed=None ):
    """
    @summary Returns a random portfolio based on certain criteria.
    @param lNum: Number of stocks to be included
    @param dtStart: Start date for portfolio
    @param dtEnd: End date for portfolio
    @param lsStocks: Optional list of ticker symbols, if not provided all symbols will be used
    @param bFilter: If False, stocks are not filtered by price or volume data, simply return random Portfolio.
    @param dmPrice: Optional price data, if not provided, data access will be queried
    @param dmVolume: Optional volume data, if not provided, data access will be queried
    @param fNonNan: Optional non-nan percent for filter, default is .95
    @param fPriceVolume: Optional price*volume for filter, default is 100,000
    @warning: Does not work for all sets of optional inputs, e.g. if you don't include dtStart, dtEnd, you need 
              to include dmPrice/dmVolume
    @return list of stocks which meet the criteria
    """
    
    if( lsStocks is None ):
        if( dmPrice is None and dmVolume is None ):
            norObj = da.DataAccess('Norgate') 
            lsStocks = norObj.get_all_symbols()
        elif( not dmPrice is None ):
            lsStocks = list(dmPrice.columns)
        else:
            lsStocks = list(dmVolume.columns)
    
    if( dmPrice is None and dmVolume is None and bFilter == True ):
        norObj = da.DataAccess('Norgate')  
        ldtTimestamps = du.getNYSEdays( dtStart, dtEnd, dt.timedelta(hours=16) )

    # if dmPrice and dmVol are provided then we don't query it every time """
    bPullPrice = False
    bPullVol = False
    if( dmPrice is None ):
        bPullPrice = True
    if( dmVolume is None ):
        bPullVol = True
            
    # Default seed (none) uses system clock """    
    rand.seed(lSeed)     
    lsRetStocks = []

    # Loop until we have enough randomly selected stocks """
    llRemainingIndexes = range(0,len(lsStocks))
    lsValid = None
    while( len(lsRetStocks) != lNum ):

        lsCheckStocks = []
        for i in range( lNum - len(lsRetStocks) ):
            lRemaining = len(llRemainingIndexes)
            if( lRemaining == 0 ):
                print 'Error in getRandPort: ran out of stocks'
                return lsRetStocks
            
            # Pick a stock and remove it from the list of remaining stocks """
            lPicked =  rand.randint(0, lRemaining-1)
            lsCheckStocks.append( lsStocks[ llRemainingIndexes.pop(lPicked) ] )

        # If bFilter is false"""
        # simply return our first list of stocks, don't check prive/vol """
        if( not bFilter ):
            return sorted(lsCheckStocks)
            

        # Get data if needed """
        if( bPullPrice ):
            dmPrice = norObj.get_data( ldtTimestamps, lsCheckStocks, 'close' )

        # Get data if needed """
        if( bPullVol ):
            dmVolume = norObj.get_data(ldtTimestamps, lsCheckStocks, 'volume' )

        # Only query this once if data is provided"""
        # else query every time with new data """
        if( lsValid is None or bPullVol or bPullPrice ):
            lsValid = stockFilter(dmPrice, dmVolume, fNonNan, fPriceVolume)
        
        for sAdd in lsValid:
            if sAdd in lsCheckStocks:
                lsRetStocks.append( sAdd )

    return sorted(lsRetStocks)
