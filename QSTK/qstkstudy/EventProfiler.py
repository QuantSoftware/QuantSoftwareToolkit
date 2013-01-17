# (c) 2011, 2012 Georgia Tech Research Corporation
# This source code is released under the New BSD license.  Please see
# http://wiki.quantsoftware.org/index.php?title=QSTK_License
# for license details.
#
# Created on October <day>,2011
# @author: Vishal Shekhar, Tucker Balch
# @contact: mailvishalshekhar@gmail.com
# @summary: Event Profiler Application
#

import pandas 
import numpy as np
import QSTK.qstkstudy.Events as ev
import matplotlib.pyplot as plt
from pylab import *
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import datetime as dt
import QSTK.qstkutil.DataAccess as da

class EventProfiler():

	def __init__(self,eventMatrix,startday,endday,\
            lookback_days = 20, lookforward_days =20,\
            verbose=False):

	    """ Event Profiler class construtor 
		Parameters : evenMatrix
			   : startday
			   : endday
		(optional) : lookback_days ( default = 20)
		(optional) : lookforward_days( default = 20)

		eventMatrix is a pandas DataMatrix
		eventMatrix must have the following structure:
		    |IBM |GOOG|XOM |MSFT| GS | JP |
		(d1)|nan |nan | 1  |nan |nan | 1  |
		(d2)|nan | 1  |nan |nan |nan |nan |
		(d3)| 1  |nan | 1  |nan | 1  |nan |
		(d4)|nan |  1 |nan | 1  |nan |nan |
		...................................
		...................................
		Also, d1 = start date
		nan = no information about any event.
		 = status bit(positively confirms the event occurence)
	    """

	    self.eventMatrix = eventMatrix
	    self.startday = startday
	    self.endday = endday
	    self.symbols = eventMatrix.columns
	    self.lookback_days = lookback_days
	    self.lookforward_days = lookforward_days
	    self.total_days = lookback_days + lookforward_days + 1
	    self.dataobj = da.DataAccess('Yahoo')
	    self.timeofday = dt.timedelta(hours=16)
	    self.timestamps = du.getNYSEdays(startday,endday,self.timeofday)
            self.verbose = verbose
            if verbose:
                print __name__ + " reading historical data"
	    self.close = self.dataobj.get_data(self.timestamps,\
                self.symbols, "close", verbose=self.verbose)
	    self.close = (self.close.fillna()).fillna(method='backfill')
	
	def study(self,filename,method="mean", \
            plotMarketNeutral = True, \
            plotErrorBars = False, \
            plotEvents = False, \
            marketSymbol='$SPX'):
	    """ 
	    Creates an event study plot
            the marketSymbol must exist in the data if plotMarketNeutral 
            is True This method plots the average of market neutral 
            cumulative returns, along with error bars The X-axis is the 
            relative time frame from -self.lookback_days to self.lookforward_days
            Size of error bar on each side of the mean value on the i 
            relative day = abs(mean @ i - standard dev @ i)
            parameters : filename. Example filename="MyStudy.pdf"
	    """

            #plt.clf()
            #plt.plot(self.close.values)
            #plt.legend(self.close.columns)
            #plt.ylim(0,2)
            #plt.draw()
            #savefig('test1.pdf',format='pdf')

            # compute 0 centered daily returns
            self.dailyret = self.close.copy() 
            tsu.returnize0(self.dailyret.values)

            # make it market neutral
	    if plotMarketNeutral:
                # assuming beta = 1 for all stocks --this is unrealistic.but easily fixable.
        	self.mktneutDM = self.dailyret - self.dailyret[marketSymbol] 
                # remove the market column from consideration
	    	del(self.mktneutDM[marketSymbol])
	    	del(self.eventMatrix[marketSymbol])
	    else:
		self.mktneutDM = self.dailyret

            # Wipe out events which are on the boundary.
            self.eventMatrix.values[0:self.lookback_days,:] = NaN
            self.eventMatrix.values[-self.lookforward_days:,:] = NaN

            # prepare to build impact matrix
            rets = self.mktneutDM.values
            events = self.eventMatrix.values
            numevents = nansum(events)
            numcols = events.shape[1]
            # create a blank impact matrix
            impact = np.zeros((self.total_days,numevents))
            currcol = 0
            # step through each column in event matrix
            for col in range(0,events.shape[1]):
                if (self.verbose and col%20==0):
                    print __name__ + " study: " + str(col) + " of " + str(numcols)
                # search each column for events
                for row in range(0,events.shape[0]):
                    # when we find an event
                    if events[row,col]==1.0:
                        # copy the daily returns in to the impact matrix
                        impact[:,currcol] = \
                            rets[row-self.lookback_days:\
                            row+self.lookforward_days+1,\
                            col]
                        currcol = currcol+1

            # now compute cumulative daily returns
            impact = cumprod(impact+1,axis=0)
            impact = impact / impact[0,:]
            # normalize everything to the time of the event
            impact = impact / impact[self.lookback_days,:]

            # prepare data for plot
            studystat = mean(impact,axis=1)
            studystd = std(impact,axis=1)
            studyrange = range(-self.lookback_days,self.lookforward_days+1)

            # plot baby
            plt.clf()
            if (plotEvents): # draw a line for each event
                plt.plot(studyrange,\
                    impact,alpha=0.1,color='#FF0000')
            # draw a horizontal line at Y = 1.0
            plt.axhline(y=1.0,xmin=-self.lookback_days,xmax=self.lookforward_days+1,\
                color='#000000')
            if plotErrorBars==True: # draw errorbars if user wants them
                plt.errorbar(studyrange[self.lookback_days:],\
                    studystat[self.lookback_days:],\
                    yerr=studystd[self.lookback_days:],\
                    ecolor='#AAAAFF',\
                    alpha=0.1)
            plt.plot(studyrange,studystat,color='#0000FF',linewidth=3,\
                label='mean')
            # set the limits of the axes to appropriate ranges
            plt.ylim(min(min(studystat),0.5),max(max(studystat),1.2))
            plt.xlim(min(studyrange)-1,max(studyrange)+1)
            # draw titles and axes
            if plotMarketNeutral:
                plt.title(('market relative mean of '+ \
                    str(int(numevents))+ ' events'))
            else:
                plt.title(('mean of '+ str(int(numevents))+ ' events'))
            plt.xlabel('Days')
            plt.ylabel('Cumulative Abnormal Returns')
            plt.draw()
            savefig(filename,format='pdf')
