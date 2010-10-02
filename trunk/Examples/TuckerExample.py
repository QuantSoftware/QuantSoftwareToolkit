'''
Created on Sep 23, 2010

@author: Shreyas Joshi
@contact: shreyasj at gatech.edu
'''

import sys
sys.path.append(str(sys.path[0])+str("/.."))
import DataAccessNew as da

listOfStocks= list()
listOfStocks.append("AMZN")
listOfStocks.append("AAPL")
listOfStocks.append ("YHOO")

listOfPaths=list()
listOfPaths.append("/hzr71/research/QSData/Processed/Norgate/Equities/US_NASDAQ/")

#Once the dates are set- this object can not give you data from outsie this range- even though it mightbe present in the hdf file- because
# we never read that data in at all. The date boundary has to be specified in UNIX timestamp since epoch.
data= da.DataAccess(True, listOfPaths, "/StrategyData", "StrategyData", True, listOfStocks, 946702800, 1262322000)

stocksToGetDataFor= list()
stocksToGetDataFor.append("BLAH")
stocksToGetDataFor.append("YHOO")


listOfTimeStamps= data.getTimestampArray() # a 1D numpy array with the timestamps, a typecast to list should convert this to a list
print "The timestamps are: "

for ts in listOfTimeStamps:
    print ts


twoDArrayOfAdjClosePrices= data.getMatrixBetweenTS(stocksToGetDataFor, "adj_close", 946962000, 1260939600)
print "The adjusted closing prices are: "
print str(twoDArrayOfAdjClosePrices)


listOfStocks= data.getListOfStocks()

print "A list of all stocks: "
print listOfStocks



