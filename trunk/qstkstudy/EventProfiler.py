import pandas 
import numpy as np
import Events as ev
import matplotlib.pyplot as plt
from pylab import *
import qstkutil.dateutil as du
import datetime as dt
import qstkutil.DataAccess as da

class EventProfiler():

	def __init__(self,eventMatrix,startday,endday,lookback_days = 20, lookforward_days =20):
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
		1 = status bit(positively confirms the event occurence)
	    """

	    self.eventMatrix = eventMatrix
	    self.startday = startday
	    self.endday = endday
	    self.symbols = eventMatrix.columns
	    self.lookback_days = lookback_days
	    self.lookforward_days = lookforward_days
	    self.total_days = lookback_days + lookforward_days + 1
	    self.dataobj = da.DataAccess('Norgate')
	    self.timeofday = dt.timedelta(hours=16)
	    self.timestamps = du.getNYSEdays(startday,endday,self.timeofday)
	    self.close = self.dataobj.get_data(self.timestamps,self.symbols, "close")
	    self.close = (self.close.fillna()).fillna(method='backfill')
	
	def grabRelativeDays(self,sequence,refloc):
	    """
	    grab a slice of the sequence around sequence[refloc]
	    If there are not enough point to be chosen for the look ahead / look back
	    we simply repeat the values.
	    In all cases the returned List will have length = lookback_days + lookforward_days + 1
	    """
	    start= max(0,refloc - self.lookback_days)
	    end = min(len(sequence) ,refloc + self.lookforward_days+1)
	    returnlist = sequence[start:end]
	    if (refloc - self.lookback_days) < 0:
	        for i in range(0,self.lookback_days - refloc):
	            returnlist.insert(0,returnlist[0])
	    if (refloc + self.lookforward_days ) >= len(sequence):
	        for i in range(end,refloc + self.lookforward_days+1 ):
	            returnlist.insert(i,returnlist[len(returnlist)-1])
	    return returnlist

	def study(self,filename,method="mean"):
	    """ This method plots the average of market neutral cumulative returns, along with error bars
		The X-axis is the relative time frame from -self.lookback_days to self.lookforward_days
		Size of error bar on each side of the mean value on the i relative day = abs(mean @ i - standard dev @ i)
		
		parameters : filename. Example filename="MyStudy.pdf"
	    """

	    dailyret = (self.close.values[1:]/self.close.values[:-1]) - 1
	    dailyret = np.insert(dailyret, 0, np.array([0.0]*len(self.symbols)), axis=0)
	    self.dailyret = dailyret
	    marketret = np.array([[np.mean(dailyret[i])]*len(dailyret[i]) for i in range(0,len(dailyret))])
	    self.marketret = marketret
	    mktneutralreturns = dailyret - marketret # assuming beta = 1 for all stocks --this is unrealistic.but easily fixable.
	    self.mktneutralreturns = mktneutralreturns
	    # Wipe out events which are on the boundary.
	    for symbol in self.symbols:
	        self.eventMatrix[symbol][0:self.lookback_days] = array([nan]*self.lookback_days)
	        self.eventMatrix[symbol][len(self.eventMatrix[symbol])-self.lookforward_days:len(self.eventMatrix[symbol])] = array([nan]*self.lookback_days)
	    # Clear out first lookback_days and last lookforward_days
	    # Akin to DB Table PK= Index( Date ): SYMBOL->MKT Neutral Return values
	    mktneutDM = pandas.DataMatrix(mktneutralreturns,self.eventMatrix.index,self.eventMatrix.columns)
	    self.mktneutDM = mktneutDM
	    # to create the impact matrix we join on the PK and iterate over symbols.
	    self.impact = []

	    for symbol in self.symbols:
	        for i in range(0,len(self.eventMatrix[symbol])):
	            if self.eventMatrix[symbol][i] == 1.0:
	                self.impact.append(self.grabRelativeDays(mktneutDM[symbol].values.tolist(), i))
	    for i in range(0,len(self.impact)):
	        self.impact[i] = [(self.impact[i][j] + 1)/(1+ self.impact[i][0]) for j in range(0,len(self.impact[i]))]
	        self.impact[i]= np.cumprod(self.impact[i])
	    print 'Total Events = ',len(self.impact)
	    
	    plt.clf()
	    self.studystatistic =[]
	    self.std = []
	    if method == "mean":
		statmethod = np.mean
	    	for i in range(0,len(self.impact[0])):
	        	self.studystatistic.append(statmethod([self.impact[j][i] for j in range (0, len(self.impact))]))
		        self.std.append(np.std([self.impact[j][i] for j in range (0, len(self.impact))]))
			self.err = [self.studystatistic[i]-self.std[i] for i in range(0, len(self.std))]
		self.err[0:self.lookback_days] = [0]*self.lookback_days # only plot uncertainity beyond day 0
	    	plt.errorbar(range(-self.lookback_days,self.lookforward_days+1),self.studystatistic,yerr=self.err,ecolor='r',label="mean w/ std err")

	    plt.legend()	    
	    plt.xlabel('Days')
	    plt.ylabel('Cumulative Returns')
	    plt.figtext(0.4,0.83,'#Events = '+str(len(self.impact)))
	    plt.draw()
	    savefig(filename,format='pdf')
