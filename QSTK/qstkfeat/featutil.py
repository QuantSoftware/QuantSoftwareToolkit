'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on Nov 7, 2011

@author: John Cornwell
@contact: JohnWCornwellV@gmail.com
@summary: Contains utility functions to interact with feature functions in features.py
'''

''' Python imports '''
import math
import pickle
import inspect
import datetime as dt
from dateutil.relativedelta import relativedelta

''' 3rd Party Imports '''
import numpy as np
import matplotlib.pyplot as plt


''' Our Imports '''
import QSTK.qstklearn.kdtknn as kdt
from QSTK.qstkutil import DataAccess as da
from QSTK.qstkutil import qsdateutil as du
from QSTK.qstkutil import tsutil as tsu

from QSTK.qstkfeat.features import *
from QSTK.qstkfeat.classes import class_fut_ret



def getMarketRel( dData, sRel='$SPX' ):
    '''
    @summary: Calculates market relative data.
    @param dData - Dictionary containing data to be used, requires specific naming: open/high/low/close/volume
    @param sRel - Stock ticker to make the data relative to, $SPX is default.
    @return: Dictionary of market relative values
    '''
    
    # the close dataframe is assumed to be in the dictionary data
    # otherwise the function will NOT WORK!
    if sRel not in dData['close'].columns:
        raise KeyError( 'Market relative stock %s not found in getMR()'%sRel )
    
    
    dRet = {}

    dfClose = dData['close'].copy()
    
    dfCloseMark = dfClose.copy()
    tsu.returnize0(  dfCloseMark.values )
    dfCloseMark = (dfCloseMark - dfCloseMark[sRel]) + 1.
    dfCloseMark.ix[0, :] = 100.
    dfCloseMark = dfCloseMark.cumprod(axis=0)
    
    #print dfCloseMark
    #Make all data market relative, except for volume
    for sKey in dData.keys():
        
        # Don't calculate market relative volume, but still copy it over 
        if sKey == 'volume':
            dRet['volume'] = dData['volume']
            continue

        dfKey = dData[sKey]
        dfRatio = dfKey/dfClose
        
        
        #Add dataFrame to dictionary to return, move to next key 
        dRet[sKey] = dfCloseMark * dfRatio
        
        #Comment the line below to convert the sRel as well, uncomment it
        #to keep the relative symbol's raw data
        dRet[sKey][sRel] = dData[sKey][sRel]

    #print dRet 
    return dRet



def applyFeatures( dData, lfcFeatures, ldArgs, sMarketRel=None, sLog=None, bMin=False ):
    '''
    @summary: Calculates the feature values using a list of feature functions and arguments.
    @param dData - Dictionary containing data to be used, requires specific naming: open/high/low/close/volume
    @param lfcFeatures: List of feature functions, most likely coming from features.py
    @param ldArgs: List of dictionaries containing arguments, passed as **kwargs
                   There is a special argument 'MR', if it exists, the data will be made market relative
    @param sMarketRel: If not none, the data will all be made relative to the symbol provided
    @param sLog: If not None, will be filename to log all of the features to 
    @param bMin: If true, only run for the last day
    @return: list of dataframes containing values
    '''



        
    ldfRet = []
    
    ''' Calculate market relative data '''
    if sMarketRel != None:
        dDataRelative = getMarketRel( dData, sRel=sMarketRel )
    
    
    ''' Loop though feature functions, pass each data dictionary and arguments '''
    for i, fcFeature in enumerate(lfcFeatures):
        #dt_start = dt.datetime.now()
        #print fcFeature, ldArgs[i], ' in:',
        ''' Check for special arguments '''
        if 'MR' in ldArgs[i]:
            
            if ldArgs[i]['MR'] == False:
                print 'Warning, setting MR to false will still be Market Relative',\
                      'simply do not include MR key in args'
        
            if sMarketRel == None:
                raise AssertionError('Functions require market relative stock but sMarketRel=None')
            del ldArgs[i]['MR']
            if bMin:
                # bMin means only calculate the LAST row of the stock
                dTmp = {}
                for sKey in dDataRelative:
                    if 'i_bars' in ldArgs[i]:
                        dTmp[sKey] = dDataRelative[sKey].ix[ 
                                     -(ldArgs[i]['lLookback'] + 
                                     ldArgs[i]['i_bars']+1):]
                    else:  
                        if 'lLookback' not in ldArgs[i]:
                            d_defaults = inspect.getargspec(fcFeature).defaults
                            d_args = inspect.getargspec(fcFeature).args
                            i_diff = len(d_args) - len(d_defaults)
                            i_index = d_args.index('lLookback') - i_diff
                            i_cut = -(d_defaults[i_index]+1)
                            dTmp[sKey] = dDataRelative[sKey].ix[i_cut:]
                            #print fcFeature.__name__ + ":" + str(i_cut)
                            
                        else:   
                            dTmp[sKey] = dDataRelative[sKey].ix[ 
                                         -(ldArgs[i]['lLookback'] + 1):]  
                ldfRet.append( fcFeature( dTmp, **ldArgs[i] ).ix[-1:] )
            else:
                ldfRet.append( fcFeature( dDataRelative, **ldArgs[i] ) )
        

                
        else:
            if bMin:
                # bMin means only calculate the LAST row of the stock
                dTmp = {}
                for sKey in dData:
                    if 'i_bars' in ldArgs[i]:
                        dTmp[sKey] = dData[sKey].ix[ 
                                     -(ldArgs[i]['lLookback'] + 
                                     ldArgs[i]['i_bars']+1):]
                       
                    else:    
                        if 'lLookback' not in ldArgs[i]:
                            d_defaults = inspect.getargspec(fcFeature).defaults
                            d_args = inspect.getargspec(fcFeature).args
                            i_diff = len(d_args) - len(d_defaults)
                            i_index = d_args.index('lLookback') - i_diff
                            i_cut = -(d_defaults[i_index]+1)
                            dTmp[sKey] = dData[sKey].ix[i_cut:]
                            #print fcFeature.__name__ + ":" + str(i_cut)
                        else:   
                            dTmp[sKey] = dData[sKey].ix[ 
                                     -(ldArgs[i]['lLookback'] + 1):]
                   
                ldfRet.append( fcFeature( dTmp, **ldArgs[i] ).ix[-1:] )
            else:
                ldfRet.append( fcFeature( dData, **ldArgs[i] ) )
        #print  dt.datetime.now() - dt_start

    
    if not sLog == None:
        with open( sLog, 'wb' ) as fFile:
            pickle.dump( ldfRet, fFile, -1 )
        
    return ldfRet

def loadFeatures( sLog ):
    '''
    @summary: Loads cached features.
    @param sLog: Filename of features.
    @return: Numpy array containing values
    '''
    
    ldfRet = []
    
    if not sLog == None:
        with open( sLog, 'rb' ) as fFile:
            ldfRet = pickle.load( fFile )
        
    return ldfRet


def stackSyms( ldfFeatures, dtStart=None, dtEnd=None, lsSym=None, sDelNan='ALL', bShowRemoved=False ):
    '''
    @summary: Remove symbols from the dataframes, effectively stacking all stocks on top of each other.
    @param ldfFeatures: List of data frames of features.
    @param dtStart: Start time, if None, uses all
    @param dtEnd: End time, if None uses all
    @param lsSym: List of symbols to use, if None, all are used.
    @param sDelNan: Optional, default is ALL: delete any rows with a NaN in it 
                    FEAT: Delete if any of the feature points are NaN, allow NaN classification
                    None: Do not delete any NaN rows
    @return: Numpy array containing all features as columns and all 
    '''
    
    if dtStart == None:
        dtStart = ldfFeatures[0].index[0]
    if dtEnd == None:
        dtEnd = ldfFeatures[0].index[-1]
    
    naRet = None
    ''' Stack stocks vertically '''
    for sStock in ldfFeatures[0].columns:
        
        if lsSym != None and sStock not in lsSym:
            continue

        naStkData = None
        ''' Loop through all features, stacking columns horizontally '''
        for dfFeat in ldfFeatures:
            
            dfFeat = dfFeat.ix[dtStart:dtEnd]
            
            if naStkData == None:
                naStkData = np.array( dfFeat[sStock].values.reshape(-1,1) )
            else:
                naStkData = np.hstack( (naStkData, dfFeat[sStock].values.reshape(-1,1)) )
   
        ''' Remove nan rows possibly'''
        if 'ALL' == sDelNan or 'FEAT' == sDelNan:
            llValidRows = []
            for i in range(naStkData.shape[0]):
                
                
                if 'ALL' == sDelNan and not math.isnan( np.sum(naStkData[i,:]) ) or\
                  'FEAT' == sDelNan and not math.isnan( np.sum(naStkData[i,:-1]) ):
                    llValidRows.append(i)
                elif  bShowRemoved:
                    print 'Removed', sStock, naStkData[i,:]
                        
            naStkData = naStkData[llValidRows,:]
            
    
        ''' Now stack each block of stock data vertically '''
        if naRet == None:
            naRet = naStkData
        else:
            naRet = np.vstack( (naRet, naStkData) )

    return naRet


def normFeatures( naFeatures, fMin, fMax, bAbsolute, bIgnoreLast=True ):
    '''
    @summary: Normalizes the featurespace.
    @param naFeatures:  Numpy array of features,  
    @param fMin: Data frame containing the price information for all of the stocks.
    @param fMax: List of feature functions, most likely coming from features.py
    @param bAbsolute: If true, min value will be scaled to fMin, max to fMax, if false,
                      +-1 standard deviations will be scaled to fit between fMin and fMax, i.e. ~69% of the values
    @param bIgnoreLast: If true, last column is ignored (assumed to be classification)
    @return: list of (weights, shifts) to be used to normalize the query points
    '''
    
    fNewRange = fMax - fMin
    
    lUseCols = naFeatures.shape[1]
    if bIgnoreLast:
        lUseCols -= 1
    
    ltRet = []
    ''' Loop through all features '''
    for i in range(lUseCols):
        
        ''' If absolutely scaled use exact min and max '''
        if bAbsolute:
            fFeatMin = np.min( naFeatures[:,i] )
            fFeatMax = np.max( naFeatures[:,i] )
        else:
            ''' Otherwise use mean +-1 std deviations for min/max (~94% of data) '''
            fMean = np.average( naFeatures[:,i] )
            fStd = np.std( naFeatures[:,i] ) 
            fFeatMin = fMean - fStd
            fFeatMax = fMean + fStd
            
        ''' Calculate multiplier and shift variable so that new data fits in specified range '''
        fRange = fFeatMax - fFeatMin
        
        if fRange == 0:
            print 'Warning, bad query data range'
            fMult = 1.
            fShigt = 0.
        else:
            fMult = fNewRange / fRange
            fShift = fMin - (fFeatMin * fMult)
        
        ''' scale and shift, save in return array '''
        naFeatures[:,i] *= fMult
        naFeatures[:,i] += fShift
        ltRet.append( (fMult, fShift) )
    
    return ltRet

def normQuery( naQueries, ltWeightShift ):
    '''
    @summary: Normalizes the queries using the given normalization parameters generated from training data.
    @param naQueries:  Numpy array of queries  
    @param ltWeightShift: List of weights and shift amounts to be applied to each query.
    @return: None, modifies naQueries
    '''
    
    assert naQueries.shape[1] == len(ltWeightShift)
    
    for i in range(naQueries.shape[1]):
        
        ''' scale and shift, save in return array '''
        naQueries[:,i] *= ltWeightShift[i][0]
        naQueries[:,i] += ltWeightShift[i][1]
        
def createKnnLearner( naFeatures, lKnn=30, leafsize=10, method='mean' ):
    '''
    @summary: Creates a quick KNN learner 
    @param naFeatures:  Numpy array of features,  
    @param fMin: Data frame containing the price information for all of the stocks.
    @param fMax: List of feature functions, most likely coming from features.py
    @param bAbsolute: If true, min value will be scaled to fMin, max to fMax, if false,
                      +-1 standard deviations will be scaled to fit between fMin and fMax, i.e. ~69% of the values
    @param bIgnoreLast: If true, last column is ignored (assumed to be classification)
    @return: None, data is modified in place
    '''
    cLearner = kdt.kdtknn( k=lKnn, method=method, leafsize=leafsize)

    cLearner.addEvidence( naFeatures )

    return cLearner

def log500( sLog ):
    '''
    @summary: Loads cached features.
    @param sLog: Filename of features.
    @return: Nothing, logs features to desired location
    '''
    
    
    lsSym = ['A', 'AA', 'AAPL', 'ABC', 'ABT', 'ACE', 'ACN', 'ADBE', 'ADI', 'ADM', 'ADP', 'ADSK', 'AEE', 'AEP', 'AES', 'AET', 'AFL', 'AGN', 'AIG', 'AIV', 'AIZ', 'AKAM', 'AKS', 'ALL', 'ALTR', 'AMAT', 'AMD', 'AMGN', 'AMP', 'AMT', 'AMZN', 'AN', 'ANF', 'ANR', 'AON', 'APA', 'APC', 'APD', 'APH', 'APOL', 'ARG', 'ATI', 'AVB', 'AVP', 'AVY', 'AXP', 'AZO', 'BA', 'BAC', 'BAX', 'BBBY', 'BBT', 'BBY', 'BCR', 'BDX', 'BEN', 'BF.B', 'BHI', 'BIG', 'BIIB', 'BK', 'BLK', 'BLL', 'BMC', 'BMS', 'BMY', 'BRCM', 'BRK.B', 'BSX', 'BTU', 'BXP', 'C', 'CA', 'CAG', 'CAH', 'CAM', 'CAT', 'CB', 'CBG', 'CBS', 'CCE', 'CCL', 'CEG', 'CELG', 'CERN', 'CF', 'CFN', 'CHK', 'CHRW', 'CI', 'CINF', 'CL', 'CLF', 'CLX', 'CMA', 'CMCSA', 'CME', 'CMG', 'CMI', 'CMS', 'CNP', 'CNX', 'COF', 'COG', 'COH', 'COL', 'COP', 'COST', 'COV', 'CPB', 'CPWR', 'CRM', 'CSC', 'CSCO', 'CSX', 'CTAS', 'CTL', 'CTSH', 'CTXS', 'CVC', 'CVH', 'CVS', 'CVX', 'D', 'DD', 'DE', 'DELL', 'DF', 'DFS', 'DGX', 'DHI', 'DHR', 'DIS', 'DISCA', 'DNB', 'DNR', 'DO', 'DOV', 'DOW', 'DPS', 'DRI', 'DTE', 'DTV', 'DUK', 'DV', 'DVA', 'DVN', 'EBAY', 'ECL', 'ED', 'EFX', 'EIX', 'EL', 'EMC', 'EMN', 'EMR', 'EOG', 'EP', 'EQR', 'EQT', 'ERTS', 'ESRX', 'ETFC', 'ETN', 'ETR', 'EW', 'EXC', 'EXPD', 'EXPE', 'F', 'FAST', 'FCX', 'FDO', 'FDX', 'FE', 'FFIV', 'FHN', 'FII', 'FIS', 'FISV', 'FITB', 'FLIR', 'FLR', 'FLS', 'FMC', 'FO', 'FRX', 'FSLR', 'FTI', 'FTR', 'GAS', 'GCI', 'GD', 'GE', 'GILD', 'GIS', 'GLW', 'GME', 'GNW', 'GOOG', 'GPC', 'GPS', 'GR', 'GS', 'GT', 'GWW', 'HAL', 'HAR', 'HAS', 'HBAN', 'HCBK', 'HCN', 'HCP', 'HD', 'HES', 'HIG', 'HNZ', 'HOG', 'HON', 'HOT', 'HP', 'HPQ', 'HRB', 'HRL', 'HRS', 'HSP', 'HST', 'HSY', 'HUM', 'IBM', 'ICE', 'IFF', 'IGT', 'INTC', 'INTU', 'IP', 'IPG', 'IR', 'IRM', 'ISRG', 'ITT', 'ITW', 'IVZ', 'JBL', 'JCI', 'JCP', 'JDSU', 'JEC', 'JNJ', 'JNPR', 'JNS', 'JOYG', 'JPM', 'JWN', 'K', 'KEY', 'KFT', 'KIM', 'KLAC', 'KMB', 'KMX', 'KO', 'KR', 'KSS', 'L', 'LEG', 'LEN', 'LH', 'LIFE', 'LLL', 'LLTC', 'LLY', 'LM', 'LMT', 'LNC', 'LO', 'LOW', 'LSI', 'LTD', 'LUK', 'LUV', 'LXK', 'M', 'MA', 'MAR', 'MAS', 'MAT', 'MCD', 'MCHP', 'MCK', 'MCO', 'MDT', 'MET', 'MHP', 'MHS', 'MJN', 'MKC', 'MMC', 'MMI', 'MMM', 'MO', 'MOLX', 'MON', 'MOS', 'MPC', 'MRK', 'MRO', 'MS', 'MSFT', 'MSI', 'MTB', 'MU', 'MUR', 'MWV', 'MWW', 'MYL', 'NBL', 'NBR', 'NDAQ', 'NE', 'NEE', 'NEM', 'NFLX', 'NFX', 'NI', 'NKE', 'NOC', 'NOV', 'NRG', 'NSC', 'NTAP', 'NTRS', 'NU', 'NUE', 'NVDA', 'NVLS', 'NWL', 'NWSA', 'NYX', 'OI', 'OKE', 'OMC', 'ORCL', 'ORLY', 'OXY', 'PAYX', 'PBCT', 'PBI', 'PCAR', 'PCG', 'PCL', 'PCLN', 'PCP', 'PCS', 'PDCO', 'PEG', 'PEP', 'PFE', 'PFG', 'PG', 'PGN', 'PGR', 'PH', 'PHM', 'PKI', 'PLD', 'PLL', 'PM', 'PNC', 'PNW', 'POM', 'PPG', 'PPL', 'PRU', 'PSA', 'PWR', 'PX', 'PXD', 'QCOM', 'QEP', 'R', 'RAI', 'RDC', 'RF', 'RHI', 'RHT', 'RL', 'ROK', 'ROP', 'ROST', 'RRC', 'RRD', 'RSG', 'RTN', 'S', 'SAI', 'SBUX', 'SCG', 'SCHW', 'SE', 'SEE', 'SHLD', 'SHW', 'SIAL', 'SJM', 'SLB', 'SLE', 'SLM', 'SNA', 'SNDK', 'SNI', 'SO', 'SPG', 'SPLS', 'SRCL', 'SRE', 'STI', 'STJ', 'STT', 'STZ', 'SUN', 'SVU', 'SWK', 'SWN', 'SWY', 'SYK', 'SYMC', 'SYY', 'T', 'TAP', 'TDC', 'TE', 'TEG', 'TEL', 'TER', 'TGT', 'THC', 'TIE', 'TIF', 'TJX', 'TLAB', 'TMK', 'TMO', 'TROW', 'TRV', 'TSN', 'TSO', 'TSS', 'TWC', 'TWX', 'TXN', 'TXT', 'TYC', 'UNH', 'UNM', 'UNP', 'UPS', 'URBN', 'USB', 'UTX', 'V', 'VAR', 'VFC', 'VIA.B', 'VLO', 'VMC', 'VNO', 'VRSN', 'VTR', 'VZ', 'WAG', 'WAT', 'WDC', 'WEC', 'WFC', 'WFM', 'WFR', 'WHR', 'WIN', 'WLP', 'WM', 'WMB', 'WMT', 'WPI', 'WPO', 'WU', 'WY', 'WYN', 'WYNN', 'X', 'XEL', 'XL', 'XLNX', 'XOM', 'XRAY', 'XRX', 'YHOO', 'YUM', 'ZION', 'ZMH']
    lsSym.append('$SPX')
    lsSym.sort()
    
    
    ''' Max lookback is 6 months '''
    dtEnd = dt.datetime.now()
    dtEnd = dtEnd.replace(hour=16, minute=0, second=0, microsecond=0)
    dtStart = dtEnd - relativedelta(months=6)
    
    
    ''' Pull in current data '''
    norObj = da.DataAccess('Norgate')
    ''' Get 2 extra months for moving averages and future returns '''
    ldtTimestamps = du.getNYSEdays( dtStart - relativedelta(months=2), \
                                    dtEnd   + relativedelta(months=2), dt.timedelta(hours=16) )
    
    dfPrice = norObj.get_data( ldtTimestamps, lsSym, 'close' )
    dfVolume = norObj.get_data( ldtTimestamps, lsSym, 'volume' )

    ''' Imported functions from qstkfeat.features, NOTE: last function is classification '''
    lfcFeatures, ldArgs, lsNames = getFeatureFuncs()                
    
    ''' Generate a list of DataFrames, one for each feature, with the same index/column structure as price data '''
    applyFeatures( dfPrice, dfVolume, lfcFeatures, ldArgs, sLog=sLog )


def getFeatureFuncs():
    '''
    @summary: Gets feature functions supported by the website.
    @return: Tuple containing (list of functions, list of arguments, list of names)
    '''
    
    lfcFeatures = [ featMA, featMA, featRSI, featDrawDown, featRunUp, featVolumeDelta, featAroon, featAroon, featStochastic , featBeta, featBollinger, featCorrelation, featPrice, class_fut_ret]
    lsNames = ['MovingAverage', 'RelativeMovingAverage', 'RSI', 'DrawDown', 'RunUp', 'VolumeDelta', 'AroonUp', 'AroonLow', 'Stochastic', 'Beta', 'Bollinger', 'Correlation', 'Price', 'FutureReturn']
      
    ''' Custom Arguments '''
    ldArgs = [ {'lLookback':30, 'bRel':False},\
               {'lLookback':30, 'bRel':True},\
               {'lLookback':14},\
               {'lLookback':30},\
               {'lLookback':30},\
               {'lLookback':30},\
               {'bDown':False, 'lLookback':25},\
               {'bDown':True, 'lLookback':25},\
               {'lLookback':14},\
               {'lLookback':14, 'sMarket':'SPY'},\
               {'lLookback':20},\
               {'lLookback':20, 'sRel':'SPY'},\
               {},\
               {'lLookforward':5, 'sRel':None, 'bUseOpen':False}]
    
    return lfcFeatures, ldArgs, lsNames
      

def testFeature( fcFeature, dArgs ):
    '''
    @summary: Quick function to run a feature on some data and plot it to see if it works.
    @param fcFeature: Feature function to test
    @param dArgs: Arguments to pass into feature function 
    @return: Void
    '''
    
    ''' Get Train data for 2009-2010 '''
    dtStart = dt.datetime(2011, 7, 1)
    dtEnd = dt.datetime(2011, 12, 31)
         
    ''' Pull in current training data and test data '''
    norObj = de.DataAccess('mysql')
    ''' Get 2 extra months for moving averages and future returns '''
    ldtTimestamps = du.getNYSEdays( dtStart, dtEnd, dt.timedelta(hours=16) )
    
    lsSym = ['GOOG']
    lsSym.append('WMT')
    lsSym.append('$SPX')
    lsSym.append('$VIX')
    lsSym.sort()
    
    lsKeys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldfData = norObj.get_data( ldtTimestamps, lsSym, lsKeys )
    dData = dict(zip(lsKeys, ldfData))
    dfPrice = dData['close']


    #print dfPrice.values
    
    ''' Generate a list of DataFrames, one for each feature, with the same index/column structure as price data '''
    dtStart = dt.datetime.now()
    ldfFeatures = applyFeatures( dData, [fcFeature], [dArgs], sMarketRel='$SPX' )
    print 'Runtime:', dt.datetime.now() - dtStart
    
    ''' Use last 3 months of index, to avoid lookback nans '''

    dfPrint = ldfFeatures[0]['GOOG']
    print 'GOOG values:', dfPrint.values
    print 'GOOG Sum:', dfPrint.ix[dfPrint.notnull()].sum()
    
    for sSym in lsSym:
        plt.subplot( 211 )
        plt.plot( ldfFeatures[0].index[-60:], dfPrice[sSym].values[-60:] )
        plt.plot( ldfFeatures[0].index[-60:], dfPrice['$SPX'].values[-60:] * dfPrice[sSym].values[-60] / dfPrice['$SPX'].values[-60] )
        plt.legend((sSym, '$SPX'))
        plt.title(sSym)
        plt.subplot( 212 )
        plt.plot( ldfFeatures[0].index[-60:], ldfFeatures[0][sSym].values[-60:] )
        plt.title( '%s-%s'%(fcFeature.__name__, str(dArgs)) )
        plt.show()


    
    
def speedTest(lfcFeature,ldArgs):
    '''
    @Author: Tingyu Zhu
    @summary: Function to test the runtime for a list of features, and output them by speed
    @param lfcFeature: a list of features that will be sorted by runtime
    @param dArgs: Arguments to pass into feature function
    @return: A list of sorted tuples of format (time, function name/param string)
    '''     

    '''pulling out 2 years data to run test'''
    daData = de.DataAccess('mysql')
    dtStart = dt.datetime(2010, 1, 1)
    dtEnd = dt.datetime(2011, 12, 31)
    dtTimeofday = dt.timedelta(hours=16)
    lsSym = ['AAPL', 'GOOG', 'XOM', 'AMZN', 'BA', 'GILD', '$SPX']

    #print lsSym

    '''set up variables for applyFeatures'''
    lsKeys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldtTimestamps = du.getNYSEdays( dtStart, dtEnd, dtTimeofday)
    ldfData = daData.get_data( ldtTimestamps, lsSym, lsKeys)
    dData = dict(zip(lsKeys, ldfData))
    
    '''loop through features'''
    ltResults = []
    for i in range(len(lfcFeature)):
        dtFuncStart = dt.datetime.now()
        ldfFeatures = applyFeatures( dData, [lfcFeature[i]], [ldArgs[i]], 
                                     sMarketRel='$SPX')
        ltResults.append((dt.datetime.now() - dtFuncStart, 
                         lfcFeature[i].__name__ + ' : ' + str(ldArgs[i])))
    ltResults.sort()
    
    '''print out result'''
    for tResult in ltResults:
        print tResult[1], ':', tResult[0]
    
    return ltResults

if __name__ == '__main__':
   
   # speedTest([featMA, featRSI, featAroon, featBeta, featCorrelation, 
   #            featBollinger, featStochastic], [{'lLookback':30}] * 7) 
   testFeature( featHiLow, {})
   pass
