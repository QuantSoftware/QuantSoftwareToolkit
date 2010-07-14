'''
Created on Jun 1, 2010

@author: Shreyas Joshi
@summary: Just a quick way to test the DataAccess class... nothing more
'''

#Due to the momentary lack of a HDF viewer that installs/works without hassle- I decided to write a little something to check if the alpha 
#values were being written properly

#Main begins
#from DataAccess import *
import DataAccess as da
import tables as pt
from itertools import izip 
import time


print "Starting..."
listOfItems=[]
listOfItems.append('symbol')
listOfItems.append('timestamp')
listOfItems.append('exchange')
listOfItems.append('adj_close')
#listOfItems.append('alphaValue')

listOfStocks=list()

#Add the names of the stocks you want, here
listOfStocks.append('AASP')
listOfStocks.append('MSFT')
listOfStocks.append("AAPL")

print listOfStocks


#alpha= da.DataAccess('trialAlpha1.h5', 'alphaData', 'alphaData', object, listOfItems)
print "\nBefore opening file"
#h5f = pt.openFile('C:\\generated data files\\newDataFile7.h5', mode = "a") # if mode ='w' is used here then the file gets overwritten!
print "Before constructor"

#"C:\\fin\\tempoutput\\" is the path to where all the hdf files are. This has to be chaanged accordingly
alpha= da.DataAccess (True, "C:\\fin\\tempoutput\\", "/StrategyData", "StrategyData", True, listOfStocks)

print "Constructor done"

listofstocks12= alpha.getListOfStocks()


    

for stock in listofstocks12:
    beta= alpha.getStockDataList(stock, 'volume')
    print str(stock) + "  " + str(len(beta))
     

#beta= alpha.getStockDataList("MSFT", 'adj_open', 1214280000, 1230699600)

print "starting getStockDataList at: " + str(time.strftime("%H:%M:%S"))
beta= alpha.getStockDataList("AAPL", 'volume')
#gamma= alpha.getStockDataList("DBX-201001", 'adj_open')
#delta= alpha.getStockDataList("PMGYF", 'adj_close')
epsilon= alpha.getStockDataList("AAPL", 'adj_close')


timestamps= alpha.getTimestampList()
print "Done getStockDataList at: " + str(time.strftime("%H:%M:%S"))

print beta.size
for (item1, item3, item2) in izip (beta, epsilon, timestamps):
    print str((time.strftime("%Y%m%d", time.gmtime(item2))))+"  "+str(item1)+"  "+str(item3)


print "Exchange is (this is just random...): " + alpha.getStaticData("AAPL", 'exchange')

#print gamma.size
#print delta.size
#print epsilon.size


#for (omega1) in izip (beta):
#    print str(omega1)
    
#for (omega1) in izip (gamma):
#    print str(omega1)
#    
#for (omega1) in izip (delta):
#    print str(omega1)
#    
#for (omega1) in izip (epsilon):
#    print str(omega1)
#    
#
#
#for (omega1, omega2, omega3, omega4) in izip (beta, gamma, delta, epsilon):
#    print str(omega1)+ "    " + str(omega2)+str(omega3)+ "    " + str(omega4)


print "All done"


#beta= alpha.getStockDataList("MSFT", "volume", None, None)
#ts= alpha.getTimestampList()
#
#for item1, item2 in izip(beta, ts):
# print str(item1)+"  "+ str(item2)
 
  
 
 
#data1= alpha.getData(None, 'volume', None, None)#[0]['symbol']
#data2= alpha.getDataList('GOOG', 'exchange',1200978000, 1200978000 )
#data3= alpha.getDataItem('GOOG', 'volume', 1200978000)
