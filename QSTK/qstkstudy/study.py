#
# Example use of the event profiler
#
import QSTK.qstkstudy.Events as ev
import datetime as dt
import QSTK.qstkstudy.EventProfiler as ep
import numpy as np

if __name__ == '__main__':
    #symbols = ['BFRE','ATCS','RSERF','GDNEF','LAST','ATTUF','JBFCF','CYVA','SPF','XPO','EHECF','TEMO','AOLS','CSNT','REMI','GLRP','AIFLY','BEE','DJRT','CHSTF','AICAF']
    #symbols = ['QQQ','AAPL','GOOG','ORCL','MSFT']
    symbols = np.loadtxt('symbol-set1.txt',dtype='S10',comments='#')
    #symbols = symbols[0:20]
    startday = dt.datetime(2008,1,1)
    endday = dt.datetime(2009,12,31)
    eventMatrix = ev.findEvents(symbols,startday,endday,verbose=True)
    eventProfiler = ep.EventProfiler(eventMatrix,startday,endday,
            lookback_days=20,lookforward_days=20,verbose=True)
    eventProfiler.study(filename="MyEventStudy.pdf",\
        plotErrorBars=True,\
        plotMarketNeutral=True,\
            plotEvents=False,\
        marketSymbol='$SPX')
    
