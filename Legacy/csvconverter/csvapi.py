import numpy as np
import dircache
from sets import Set
import time
import tables as pt
import sys
import time
import os
from optparse import OptionParser

class TimestampsModel (pt.IsDescription):
    timestamp = pt.Time64Col()
#class TimestampsModel ends

class StrategyDataModel(pt.IsDescription):
    symbol = pt.StringCol(30)           #30 char string; Ticker
    exchange = pt.StringCol(10)         #10 char string; NYSE, NASDAQ, etc.
    adj_high = pt.Float32Col()
    adj_low = pt.Float32Col()
    adj_open = pt.Float32Col()
    adj_close = pt.Float32Col()
    close = pt.Float32Col()
    volume = pt.Float32Col()  #Changing from Int32Col()
    timestamp = pt.Time64Col()
    date = pt.Int32Col()
    interval = pt.Time64Col()
#class StrategyDataModel done
    
class StockPriceData:
    def __init__(self):
        self.filt_list=[]
        self.timestamps=[]
        
    def getSymbols(self, listOfPaths, fileExtensionToRemove):
        '''
        @bug: This might not work if the path contains a folder whose name has .csv, or is some random file that has a .csv in it..
               So, lets assume that whoever is using this is not going to "cheat" us
        '''
        listOflistOfStocks=list()
        for path in listOfPaths:
            stocksAtThisPath=list ()
            stocksAtThisPath= dircache.listdir(str(path))
            #Next, throw away everything that is not a .csv And these are our stocks!
            stocksAtThisPath = filter (lambda x:(str(x).find(str(fileExtensionToRemove)) > -1), stocksAtThisPath)
            #Now, we remove the .csv to get the name of the stock
            stocksAtThisPath = map(lambda x:(x.partition(str(fileExtensionToRemove))[0]),stocksAtThisPath)
            
            #Then add that list to listOflistOfStocks
            listOflistOfStocks.append(stocksAtThisPath)       
        return listOflistOfStocks       
        #getSymbols done
   
#build the array
    def getData(self, listOfListOfStocks, listOfInputPaths, startDate, endDate, listOfOutputPaths):
        '''
        @summary: This is where all the work happens
        @attention: Assumption here is that past data never changes
        @bug: The exchange is currently set pretty randomly
        '''

        #Finding no. of stocks
        noOfStocks=0        
        for stock_list in listOfListOfStocks:
            noOfStocks+= len (stock_list)
            #for stock in stock_list:
                #print str(stock)
        
        print "No. of stocks: " + str(noOfStocks)
        print "No. of timestamps: " +  str(len(self.timestamps))

        
        listIndex=-1
        ctr=1;
        for inputFileFolder in listOfInputPaths:
          listIndex+=1
          outputFileFolder= str(listOfOutputPaths[listIndex])
          stocks_list= listOfListOfStocks[listIndex]
          for i in range(0, len(stocks_list)): # - self.count_of_non_existent_stocks):
                print str(stocks_list[i]) +"   "+str(ctr)+" of "+ str(noOfStocks)+"  "+ str(time.strftime("%H:%M:%S"))
                ctr= ctr+1
                
                beginTS= startDate
                
                #Check if the file exists
                if (os.path.exists(str(outputFileFolder) + str(stocks_list[i]+".h5"))):
                    
                     #Checking the last timestamp in the hdf file               
                    h5f=pt.openFile(outputFileFolder + str(stocks_list[i]+".h5"), mode = "a")
                    print "Updating " +str(outputFileFolder + str(stocks_list[i]+".h5"))
                    table= h5f.getNode('/StrategyData', 'StrategyData')
                    beginTS= int(time.strftime("%Y%m%d", time.gmtime(table[table.nrows-1]['timestamp']))) #+ 1 #POSSIBLE BUG?
                    if (str(beginTS) >= self.timestamps[len(self.timestamps)-1]): #if (os.path.getmtime(str(outputFileFolder)+str(stocks_list[i])+".h5") > os.path.getmtime(str(self.dirname+ "/"+ str(stocks_list[i]+".CSV")))):
                        #The hdf5 file for this stock has been modified after the CSV file was modified. Ergo- no changes need to be made to it now..
                        print str(stocks_list[i])+".h5 already is up to date. "+ str(time.strftime("%H:%M:%S"))
                        h5f.close()
                        continue
                    else:
                        #File is present but not upto date
                         beginTS= int(time.strftime("%Y%m%d", time.gmtime(table[table.nrows-1]['timestamp']))) 
                else:
                    #The only foreseeable reason why there might be an exception here is that the hdf file does not exist. So, creating it.
                    print "Creating file: " + str(outputFileFolder) + str(stocks_list[i]+".h5")+"  "+ str(time.strftime("%H:%M:%S"))
                    
                    h5f = pt.openFile(str(outputFileFolder) + str(stocks_list[i]+".h5"), mode = "w")
                    group = h5f.createGroup("/", 'StrategyData')
                    table = h5f.createTable(group, 'StrategyData', StrategyDataModel)
                    beginTS= startDate
                    #else done
          
                f=open(str(inputFileFolder)+str(stocks_list[i]+str(".CSV")))
                jk=f.readlines()
                f.close()
                jk.pop(0)
                
                self.filt_list=list()
                filt_list_temp=filter(lambda x: (int(x.split(',')[1])> int(beginTS)) ,jk) #Because we only want timestamps strictly greater than the last timestamp currently in the file.
                filt_list_temp=filter(lambda x: (int(x.split(',')[1])<= int(endDate)) ,filt_list_temp)
                filt_list_temp=map(lambda x:(x.split(',')[0],x.split(',')[1],x.split(',')[2],x.split(',')[3],x.split(',')[4],x.split(',')[5],x.split(',')[6],(x.split(',')[7]).strip()),filt_list_temp)
                
                self.filt_list.append(filt_list_temp)

                if (table.nrows > 0):
                    #we are appending to an old file and not creating a new file..

                    tsStartIndex= np.array(self.timestamps).searchsorted(beginTS) +1
                    
                else:
                    #creating a new file...
                    tsStartIndex =0
                #if (table.nrows > 0) done
                
                k = 0
                for j in range(tsStartIndex, len(self.timestamps)):
                    if (k< len(self.filt_list[0])):
                                            
                     if((self.timestamps[j])< (self.filt_list[0][k][1])):
                        row=table.row 
                        row['exchange'] = 'NYSE'
                        row['symbol'] = self.filt_list[0][k][0]
                        row['adj_open'] = np.NaN 
                        row['adj_close'] = np.NaN
                        row['adj_high'] = np.NaN
                        row['adj_low'] = np.NaN
                        row['close'] = np.NaN
                        row['volume'] = np.NaN
                        parseddate = time.strptime(self.timestamps[j],'%Y%m%d')
#                        row['date'] = self.timestamps[j]
                        row['timestamp'] = time.mktime(parseddate)
                        row.append()
                         
                     elif(self.timestamps[j]==self.filt_list[0][k][1]):
                        row=table.row 
                        row['exchange'] = 'NASDAQ'
                        row['symbol'] = self.filt_list[0][k][0]
                        row['adj_open'] = float(self.filt_list[0][k][2]) 
                        row['adj_close'] = float(self.filt_list[0][k][5])
                        row['adj_high'] = float(self.filt_list[0][k][3])
                        row['adj_low'] = float(self.filt_list[0][k][4])
                        row['close'] = float(self.filt_list[0][k][7])
                        row['volume'] = int(self.filt_list[0][k][6])
                        parseddate = time.strptime(self.timestamps[j],'%Y%m%d')
#                        row['date'] = self.timestamps[j]
                        row['timestamp'] = time.mktime(parseddate)
                        row.append()

                        k=k+1 
                     else:
                         print"###############Something has gone wrong. A stock had a timestamp which was not in the timestamp list..."
                         print "TS: " + str(self.timestamps[j]) + ", Stock: " + str (self.filt_list[0][k][1]) 
                         k=k+1
                         #should stop executing here? Naah
#                         sys.exit()
            
                    else:
                        row=table.row 
                        row['exchange'] = 'NYSE'
                        row['symbol'] = stocks_list[i] #self.filt_list[0][len(self.filt_list[0])-1][0] ####NOTE. POSSIBLE BUG?
                        row['adj_open'] = np.NaN 
                        row['adj_close'] = np.NaN
                        row['adj_high'] = np.NaN
                        row['adj_low'] = np.NaN
                        row['close'] = np.NaN
                        row['volume'] = np.NaN
                        parseddate = time.strptime(self.timestamps[j],'%Y%m%d')
#                        row['date'] = self.timestamps[j]
                        row['timestamp'] = time.mktime(parseddate)
#                        row['interval'] = 86400
                        row.append()
            
                #for j in range(len(self.timestamps)) ends
                table.flush()
                h5f.close()   
            #for i in range(0, stocks.size) done
        
        print "Writing data done. "+ str(time.strftime("%H:%M:%S"))
        

    def makeOrUpdateTimestampsFile(self, fileName, listOflistOfStocks, listOfInputPaths, startDate, endDate):
        '''
        @bug: Formerly did not take care of DST
        @attention: fixed DST bug. No known DST problems now.
        '''
        
        DAY=86400
        
        if (os.path.exists(fileName)):
           print "Updating timestamps"
           h5f = pt.openFile(str(fileName), mode = "a")
           table=h5f.getNode('/timestamps','timestamps')
                      
           lastTSFromFile= str(time.strftime("%Y%m%d", time.gmtime(table[table.nrows-1]['timestamp'])))
           
           if (str(startDate)<= lastTSFromFile):
               startDate=str(time.strftime("%Y%m%d", time.gmtime(table[table.nrows-1]['timestamp']))) # TO FIX DST BUG
               
        else:
           print "Creating new timestamp file"
           h5f = pt.openFile(str(fileName), mode = "w")
           group = h5f.createGroup("/", 'timestamps')
           table = h5f.createTable(group, 'timestamps', TimestampsModel)
           
        print "start: " + str(startDate)+", end: "+ str(endDate)
        
        tslist=list()    
        ctr=1
        if (str(startDate) <= str(endDate)):
           listIndex=-1
           for path in listOfInputPaths:
             listIndex+=1
             for stock in listOflistOfStocks[listIndex]:
                #print str(stock)+" "+str(ctr)+"  "+str(time.strftime("%H:%M:%S")) 
                ctr+=1
                           
                f=open(str(path)+str(stock+str(".CSV")))
                j=f.readlines()
                j.pop(0) #To remove the "header" row
                f.close()
                
                filt_list_temp=filter(lambda x: (int(x.split(',')[1])> int(startDate)) ,j) # To fix DST bug
                filt_list_temp=filter(lambda x: (int(x.split(',')[1])<= int(endDate)) ,filt_list_temp)

                if not (filt_list_temp):
                    print str(stock.split('.')[0]) + " didn't exist in this period\n"
                    #ENHANCEMENT- CAN ALSO REMOVE STOCK FROM THE STOCKLIST
                    #This can not be done right now- because if a stock did not exist- but another stock did exist then NaNs have to be added to the stock that did not exist.
                else:
                     #it existed and now we need the timestamps
                     filt_list_temp=map(lambda x:(x.split(',')[1]),filt_list_temp)
                     filt_list_temp= map(lambda item:(time.mktime(time.strptime(item,'%Y%m%d'))), filt_list_temp)

                     for item in filt_list_temp:
                        try:
                          tslist.index(int(item))
                        except:
                          tslist.append(int(item))
                          
                          
                if (len(tslist)>0):
                   if (self.continueChecking(tslist, startDate, endDate)== False):
                       break   #All dates are covered..       
                
                #for stock in stocks_list done           
        
        tslist.sort() #this should all fit into memory
        
        for ts in tslist:
            row= table.row
            row['timestamp']= ts
            #print "Adding timestamp " + str (ts)
            row.append()
            #for ts in tslist ends
            
        table.flush()
        h5f.close()    
        
        #makeTimestampsFile ends

        
    def continueChecking(self, tsList, beginTS, endTS):
        '''
        @summary: This function basically checks if a day that we haven't found any trades on is a weekend. If so- we don't need to keep looking. The converter will work just fine even without this function- but it will take more time- because it will keep looking for timestamps that it is not going to find.
        @bug: There is a Daylight savings time bug here too- but it won't adversely affect anything because DST always happens over the weekends! Though if the time change happens on a weekday sometime in the distant past/future this function may break.
        '''
        
        index=1
        DAY=86400
        
        while (index < len(tsList)):
            if (int(tsList[index])- int(tsList[index -1]) > DAY):
                tempTS= tsList[index-1] + DAY
                while (tempTS< tsList[index]):
                    timeStruct= time.gmtime(tempTS)
                    if not ((timeStruct[6] == 5) or (timeStruct[6] == 6)):
                        #Keep looking
                        return True #if its not a Saturday or a Sunday then keep looking
                    tempTS+=DAY
                    #while (tempTS< tsList[index]) ends
            index+=1        
            #while ends
        #Checking from beginTS to start of list
        tempTS=time.mktime(time.strptime(str(beginTS),'%Y%m%d'))
        
        while (int(tsList[0])- int(tempTS) > DAY):
            timeStruct= time.gmtime((tempTS))
            if not ((timeStruct[6] == 5) or (timeStruct[6] == 6)):
                return True
                #if not... ends    
            tempTS+=DAY
            #while (tsList[0]- tempTS > DAY) ends
        #Checking from endTS to end of list
        tempTS=time.mktime(time.strptime(str(endTS),'%Y%m%d'))
        
        while (int(tempTS)- int(tsList[len(tsList)-1]) > DAY):
            timeStruct= time.gmtime(tempTS)
            if not ((timeStruct[6] == 5) or (timeStruct[6] == 6)):
                return True
                #if not... ends    
            tempTS+=DAY
            #while (tempTS- tsList[len(tsList)-1] > DAY) ends
        
        print "Smartly figured out that we don't need to continue"
        return False #stop looking for more timestamps because all the timestamps that can be in the list are now there..
                     #we will not get any more timestamps by looking for more..because there just aren't any left... cool huh?    
        #continueChecking ends    
        
        
    def readTimestampsFromFile(self, fileName, beginTS, endTS):
        h5f = pt.openFile(str(fileName), mode = "a")
        fileIterator= h5f.root.timestamps.timestamps
        
        tslist=[]
        for row in fileIterator.iterrows():
            temp= str(time.strftime("%Y%m%d", time.gmtime(row['timestamp'])))
            
            if (temp>= str(beginTS)) and (temp <= str(endTS)):
              tslist.append(temp)
              
            if (temp > str(endTS)):
                break
            
        h5f.close()
        
        self.timestamps=tslist
        #readTimestampsFromFile ends
     
    def keepHDFFilesInSyncWithCSV(self, listOfInputPaths, listOfOutputPaths):
        '''
        @summary: This function removes HDF files that correspond to CSV files that existed in the past- but don't exist anymore. Possibly because the stock was delisted or something like that. 
        '''
        print "Removing HDF files for which there is no corresponding CSV file"
        listOfListOfHdfFiles=self.getSymbols(listOfOutputPaths, ".h5")
        listOfListOfCsvFiles=self.getSymbols(listOfInputPaths, ".csv") #I guess this isn't really necessary, we could just reuse the stock list or something
                                                           #but let's just keep things "proper"
        ctr=-1
        for listofHDFFiles in listOfListOfHdfFiles:
              ctr+=1
              for hdfFile in listofHDFFiles:
                  try:
                    #Check if the HDF file exists...
                    listOfListOfCsvFiles[ctr].index(hdfFile)
                  except:   
                      print "Removing "+str(listOfOutputPaths[ctr]) + str(hdfFile)+".h5"
                      os.remove(str(listOfOutputPaths[ctr]) + str(hdfFile)+".h5")
                      #if ends
                  #for hdfFile in listOfListOfHdfFiles ends
              #for listofHDFFiles in listOfListOfHdfFiles ends
        
        print "Done removing HDF files (if any)"
        #keepHDFFilesInSyncWithCSV done
                

         
if __name__ == "__main__":
    '''
    @attention: The HDF file containing the timestamps should not be in any of the output paths because, if it is, then it will be deleted at the end.
    '''
    
    print "Starting..."+ str(time.strftime("%H:%M:%S"))
    
    parser = OptionParser()
    args = parser.parse_args()[1]
    endDate= args[0]
    print "End date is: " + str (endDate)
    
    
    #Date to start reading data Format: YYYYMMDD
    startDate = 19840101
    
    #Date to end reading data Format: YYYYMMDD
    #endDate = 20100831
    
    #The complete path to the file containing the list of timestamps. This should not be in the output folder because it will be removed by the keepHDFFilesInSyncWithCSV function!
    timestampsFile="C:\\generated data files\\timestamp files\\timestamps.h5"
    
    
    spd = StockPriceData()
    
    #Remember the '\\' at the end...
    listOfInputPaths= list()
    listOfInputPaths.append("C:\\Trading data text\\Stocks\\Delisted Securities\\US Recent\\")
    listOfInputPaths.append ("C:\\Trading data text\\Stocks\\US\\AMEX\\")
    listOfInputPaths.append ("C:\\Trading data text\\Stocks\\US\\Delisted Securities\\")
    listOfInputPaths.append ("C:\\Trading data text\\Stocks\\US\OTC\\")
    listOfInputPaths.append ("C:\\Trading data text\\Stocks\\US\\NASDAQ\\")
    listOfInputPaths.append ("C:\\Trading data text\\Stocks\\US\NYSE\\")
    listOfInputPaths.append ("C:\\Trading data text\\Stocks\\US\\NYSE Arca\\")
    
    listOfOutputPaths= list()
    listOfOutputPaths.append("C:\\generated data files\\one stock per file\\maintain folder structure\\Delisted_US_Recent\\")
    listOfOutputPaths.append("C:\\generated data files\\one stock per file\\maintain folder structure\\US_AMEX\\")
    listOfOutputPaths.append("C:\\generated data files\\one stock per file\\maintain folder structure\\US_Delisted\\")
    listOfOutputPaths.append("C:\\generated data files\\one stock per file\\maintain folder structure\OTC\\")
    listOfOutputPaths.append("C:\\generated data files\\one stock per file\\maintain folder structure\\US_NASDAQ\\")
    listOfOutputPaths.append("C:\\generated data files\\one stock per file\\maintain folder structure\\US_NYSE\\")
    listOfOutputPaths.append("C:\\generated data files\\one stock per file\\maintain folder structure\\US_NYSE Arca\\")
    
    #If the output paths don't exist, then create them...
    for path in listOfOutputPaths:
        if not (os.access(path, os.F_OK)):
            #Path does not exist, so create it
            os.makedirs(path)
    #done making all output paths!        
    
    if (len(listOfInputPaths)!= len(listOfOutputPaths)):
        print "No. of input paths not equal to the number of output paths.. quitting"
        sys.exit("FAILURE")
    listOfListOfStocks=spd.getSymbols(listOfInputPaths, ".csv")
    
    
    if(endDate<startDate):
        print "Error: enddate earlier than startdate"
        sys.exit(0)
        
    spd.makeOrUpdateTimestampsFile(timestampsFile, listOfListOfStocks, listOfInputPaths, startDate, endDate)
    spd.readTimestampsFromFile(timestampsFile, startDate, endDate) 
    spd.getData(listOfListOfStocks, listOfInputPaths, startDate, endDate, listOfOutputPaths)
    spd.keepHDFFilesInSyncWithCSV(listOfInputPaths, listOfOutputPaths)
    
    print "All Done. Conversion from CSV to HDF5 is complete."
