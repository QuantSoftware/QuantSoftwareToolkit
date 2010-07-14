import numpy as np
import dircache
from sets import Set
import time
import tables as pt
import sys
import time
import os

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
    def __init__(self,dirname):
        self.dirname=dirname
        self.list_user_file_names = []
        self.filt_list=[]
        self.startDate = 0
        self.endDate= 0
        self.count_of_non_existent_stocks = 0
        self.priceArray = np.ndarray( shape=(0,0), dtype=np.object)
        self.stocks_list = []
        self.timestamps=[]
        #self.signalsArray = XXX
        
#used to get the symbols from the allcsv directory
    def getSymbols(self):
        list_file_names=dircache.listdir(self.dirname)
        list_file_names_strip_txt = map(lambda x:(x.partition('.csv')[0]),list_file_names)
        return list_file_names
       # print list_file_names_strip_txt

#used to get all the dates a particular stock has been traded
    def getCalendar(self,symbol):
        symbol = str(symbol).upper() + ".CSV"  #Changed from .TXT
        f=open(str(self.dirname)+"/"+str(symbol))
        j=f.readlines()
        f.close()
#        j=j[1:len(j)]
        j.pop(0) #To remove the "header" row
        stock_trading_days=map(lambda x:(x.split(',')[1]),j)
        #print stock_trading_days
        return stock_trading_days


#used to get the prices for a subset of days for the stock
    def getSelectedPrices(self,symbol):
        symbol = str(symbol).upper() + ".TXT"
        f=open(str(self.dirname)+"/"+str(symbol))
        j=f.readlines()
        f.close()
#        j=j[1:len(j)]
        j.pop(0) #To remove the "header" row
        stock_trading_days=map(lambda x:(x.split(',')[1]),j)
       # print stock_trading_days
        return stock_trading_days




# to get the user specified symbols       
    def getUserSymbols(self,filename):
        f=open(filename)
        list_user_tickers=f.readlines()
        f.close()
        for i in range(0,len(list_user_tickers)):
            list_user_tickers[i]=list_user_tickers[i].strip()
            #stocks_list.append(list_user_tickers[i].upper())
            list_user_tickers[i]=str(list_user_tickers[i]).upper()+".CSV" #Changed to CSV from TXT
       # print "user_tickers" + str(list_user_tickers)
        return list_user_tickers

# to find intersection of user specified symbols and allsymbols to leave out type etc
    def getMySymbols(self,filename):
        
        print "In function getMySymbols" 
        
        a=Set(self.getSymbols())
#        b=Set(self.getUserSymbols(filename))
        
#        print "a: " + str(a)
#        print "b: " + str(b)
        
#        c=a.intersection(b)
        c=a 
        list_user_file_names=list(c)
        list_user_file_names.sort()
        self.list_user_file_names = list_user_file_names
        
#        print "len(self.list_user_file_names)" + str(len(self.list_user_file_names))
        
        list_user_file_names_strip_txt = map(lambda x:(x.partition('.csv')[0]),list_user_file_names)
        #print "strip_txt" + str(list_user_file_names_strip_txt)
        print "getMySymbols done"
        return self.list_user_file_names

#get the stock list
    def getStocksList(self,filename):
        sym=self.getMySymbols(filename)
        self.stocks_list = map(lambda x:(x.partition('.csv')[0]),sym)
        #print "stocks_list" + str(stocks_list)
        return self.stocks_list


#get the time stamp
    def getTimeStamp(self,startDate,endDate):
        print "start and end dates: " + str (startDate)+ "    " + str(endDate)
        self.constructFilteredList(startDate,endDate)
        date_sorted = []
        print "len(self.filt_list): " + str(len(self.filt_list))
        for i in range(0,len(self.filt_list)):
            date_sorted.append(int(self.filt_list[i][0][1]))
            

        csv_date = -1     
        
#        print "len date_sorted: " + str (len(date_sorted))
        for i in range(0,len(date_sorted)):
            
#            print "min: " + str(min(date_sorted)) + str(" current date: ") + date_sorted[i] 
            if(min(date_sorted)==date_sorted[i]):
                csv_date = i
                break
       # print "hellooooo" + str(csv_date)
        timestamp_list = []
        print "csv_date is: " + str (csv_date)
        if(csv_date!=-1):
            print "len filt_list: " + str (len(self.filt_list[csv_date]))
            
            for i in range(0,len(self.filt_list[csv_date])):
                temp=[]
                temp.append(self.filt_list[csv_date][i][1])
                timestamp_list.append(temp)        
        print "timestamp list is: " + str(timestamp_list)
        timestamp_list = map(lambda x: x[0],timestamp_list)
        return timestamp_list
        
# get an intermediate list (which is required by all classes-to make the extraction faster)           
    def constructFilteredList(self,startDate,endDate):
        
        print "In constructFilteredList " +"  "+ str(time.strftime("%H:%M:%S"))
        self.startDate = startDate
        self.endDate = endDate
        i=0
#        user_file_names_extract_data=self.list_user_file_names
               
        print "len of user_file_names_extract_data: " + str(len(self.list_user_file_names))
        for x in self.list_user_file_names:
            f=open(str(self.dirname)+"/"+str(x))
            j=f.readlines()
            f.close()
#            j=j[1:len(j)]
            j.pop(0) #To remove the "header" row 
            
            filt_list_temp=filter(lambda x: (int(x.split(',')[1])>= int(self.startDate)) ,j)
            filt_list_temp=filter(lambda x: (int(x.split(',')[1])<= int(self.endDate)) ,filt_list_temp)
            if not (filt_list_temp):
                print str(x.split('.')[0]) + " didn't exist in this period\n"
                self.stocks_list.remove(x.partition('.csv')[0])
#                filt_list_temp=map(lambda x:(x.split(',')[0],x.split(',')[1],x.split(',')[2],x.split(',')[3],x.split(',')[4],x.split(',')[5],x.split(',')[6],(x.split(',')[7]).strip()),filt_list_temp)
#                self.filt_list.append(filt_list_temp)
            else:
                 #it existed and now we need the timestamps
                 filt_list_temp=map(lambda x:(x.split(',')[1]),filt_list_temp)
                 
#                 print "filt_list_temp: "+ str(filt_list_temp)
                 for item in filt_list_temp:
                    try:
                      self.timestamps.index(item)
                    except:
                      self.timestamps.append(item) 
        
        self.timestamps.sort()
        print "constructFilteredList done" +"  "+ str(time.strftime("%H:%M:%S"))
        return self.filt_list




#build the array
    def getData(self,stocks_list, startDate, endDate, outputFileFolder):
        '''
        @summary: This is where all the work happens
        @attention: Assumption here is that past data never changes
        '''
        
#        self.constructFilteredList (startDate, endDate)
        
        
        #Now begins the painful process of going through all the stocks and checking for timestamps
        print "In getData"
            
            
        
#        print "The timestamp values are: "
#        for i in range (0, len(self.timestamps)):
#            print self.timestamps[i]
#        
#        print "Printing timestamps done"
        
        
        
#        stocks = np.array(stocks_list)
        
#        self.priceArray = np.ndarray( shape=(timestamps.size, stocks.size), dtype=np.object)
        print "No. of stocks: " + str(len(stocks_list))
        print "No. of timestamps: " +  str(len(self.timestamps))
        
        print "The stocks are:"
        for stock1 in stocks_list:
         print stock1
        print "printed all stocks"
        
        print "Writing data to file"+"  "+ str(time.strftime("%H:%M:%S"))
        
        for i in range(0, len(stocks_list)): # - self.count_of_non_existent_stocks):
            print str(stocks_list[i]) +"   "+str(i+1)+" of "+ str(len(stocks_list))+"  "+ str(time.strftime("%H:%M:%S"))
            
            
            beginTS= startDate
            
#            try:
            #Check if the file exists
            if (os.path.exists(str(outputFileFolder) + str(stocks_list[i]+".h5"))):
                
                 #Checking the last timestamp in the hdf file               
                h5f=pt.openFile(outputFileFolder + str(stocks_list[i]+".h5"), mode = "a")
                print "Updating " +str(outputFileFolder + str(stocks_list[i]+".h5"))
                table= h5f.getNode('/StrategyData', 'StrategyData')
#                tsVal= table[table.nrows-1]['timestamp']
                beginTS= int(time.strftime("%Y%m%d", time.gmtime(table[table.nrows-1]['timestamp']))) #+ 1 #POSSIBLE BUG?
#                print "beginTS: "+ str(beginTS)+", self.timestamps[len(self.timestamps)-1]: "+str(self.timestamps[len(self.timestamps)-1])
                if (str(beginTS) >= self.timestamps[len(self.timestamps)-1]): #if (os.path.getmtime(str(outputFileFolder)+str(stocks_list[i])+".h5") > os.path.getmtime(str(self.dirname+ "/"+ str(stocks_list[i]+".CSV")))):
                    #The hdf5 file for this stock has been modified after the CSV file was modified. Ergo- no changes need to be made to it now..
                    print str(stocks_list[i])+".h5 already is up to date. "+ str(time.strftime("%H:%M:%S"))
                    h5f.close()
                    continue
                else:
                    #File is present but not upto date
                     beginTS= int(time.strftime("%Y%m%d", time.gmtime(table[table.nrows-1]['timestamp'])))+ 1 #POSSIBLE BUG?
                     #This is so that the filt_list_temp=filter(lambda x: (int(x.split(',')[1])>= int(beginTS)) ,jk)  line 
                     #(which come a few lines later)
                     #catches only the data that is to be added and not the last row of the previous data
            else:
                #The only foreseeable reason why there might be an exception here is that the hdf file does not exist. So, creating it.
                print "Creating file: " + str(outputFileFolder) + str(stocks_list[i]+".h5")+"  "+ str(time.strftime("%H:%M:%S"))
                
                h5f = pt.openFile(str(outputFileFolder) + str(stocks_list[i]+".h5"), mode = "w")
                group = h5f.createGroup("/", 'StrategyData')
                table = h5f.createTable(group, 'StrategyData', StrategyDataModel)
                beginTS= startDate
                #except done
      
                    


            f=open(str(self.dirname)+"/"+str(stocks_list[i]+str(".CSV")))
            jk=f.readlines()
            f.close()
            jk.pop(0)
#            jk=jk[1:-1]
            
            self.filt_list=list()
            filt_list_temp=filter(lambda x: (int(x.split(',')[1])>= int(beginTS)) ,jk) 
            filt_list_temp=filter(lambda x: (int(x.split(',')[1])<= int(endDate)) ,filt_list_temp)
            filt_list_temp=map(lambda x:(x.split(',')[0],x.split(',')[1],x.split(',')[2],x.split(',')[3],x.split(',')[4],x.split(',')[5],x.split(',')[6],(x.split(',')[7]).strip()),filt_list_temp)
            
            self.filt_list.append(filt_list_temp)
#            if (len(filt_list_temp)>0):
#              self.filt_list.append(filt_list_temp)
#            else:
#              h5f.close() 
##              print "QUITTING" 
#              continue   
            
            
            
#            print self.filt_list
            
            
            if (table.nrows > 0):
                #we are appending to an old file and not creating a new file..
#                print "Appending to old file"
                
                tsStartIndex= len(self.timestamps) -1
#                beginTS-=1
                while ((tsStartIndex > 0) and (str(beginTS) < self.timestamps[tsStartIndex])):
                    tsStartIndex -= 1
                
#                if (tsStartIndex+1 < len(self.timestamps) -1):
#                   tsStartIndex+=1 
                
            else:
                #creating a new file...
#                print "Creating a new file"  
                tsStartIndex =0  
            
            k = 0
#            print "tsStartIndex: " + str(tsStartIndex) + "ts there: " + str(self.timestamps[tsStartIndex])
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
                    row['date'] = self.timestamps[j]
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
                    row['date'] = self.timestamps[j]
                    row['timestamp'] = time.mktime(parseddate)
                    row['interval'] = 86400
                    row.append()

                    k=k+1 
                 else:
                     print"###############Something has gone wrong. A stock had a timestamp which was not in the timestamp list..."
                     print "TS: " + str(self.timestamps[j]) + ", Stock: " + str (self.filt_list[0][k][1]) 
                     k=k+1
                     #should stop executing here
#                     sys.exit()
        
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
                    row['date'] = self.timestamps[j]
                    row['timestamp'] = time.mktime(parseddate)
                    row['interval'] = 86400
                    row.append()
        
            #for j in range(len(self.timestamps)) ends
            table.flush()
            h5f.close()   
        #for i in range(0, stocks.size) done
        
        print "Wrting data done. "+ str(time.strftime("%H:%M:%S"))
        

    def makeOrUpdateTimestampsFile(self, fileName, stocks_list, startDate, endDate):
        
        print "In makeTimestampsFile..." + str(time.strftime("%H:%M:%S"))
        DAY=86400
        
        if (os.path.exists(fileName)):
           print "Updating timestamps"
           h5f = pt.openFile(str(fileName), mode = "a")
           table=h5f.getNode('/timestamps','timestamps')
                      
           lastTSFromFile= str(time.strftime("%Y%m%d", time.gmtime(table[table.nrows-1]['timestamp'])))
           print "startDate: " + str(startDate) + ",   "+lastTSFromFile
           
           if (str(startDate)<= lastTSFromFile):
               startDate=str(time.strftime("%Y%m%d", time.gmtime(table[table.nrows-1]['timestamp']+ DAY)))
               print "startDate is now: " + startDate
#               print "last ts from file: " + tempDate
#               startDate= int(time.strftime("%Y%m%d", time.gmtime(table[table.nrows-1]['timestamp'])))  #make sure we don't add the same timestamps twice...
           
        else:   
           print "Creating new timestamp file"
           h5f = pt.openFile(str(fileName), mode = "w")
           group = h5f.createGroup("/", 'timestamps')
           table = h5f.createTable(group, 'timestamps', TimestampsModel)
           
        
        print "start: " + str(startDate)+", end: "+ str(endDate)
        
        tslist=list()    
        ctr=1
        if (str(startDate) <= str(endDate)):
          for stock in stocks_list:
            print str(stock)+" "+str(ctr)+" of "+str(len(stocks_list)) + "  "+str(time.strftime("%H:%M:%S"))
            ctr+=1
                       
            f=open(str(self.dirname)+"/"+str(stock+str(".CSV")))
            j=f.readlines()
            j.pop(0) #To remove the "header" row
            f.close()
            
            filt_list_temp=filter(lambda x: (int(x.split(',')[1])>= int(startDate)) ,j)
            filt_list_temp=filter(lambda x: (int(x.split(',')[1])<= int(endDate)) ,filt_list_temp)

            if not (filt_list_temp):
                print str(stock.split('.')[0]) + " didn't exist in this period\n"
                #ENHANCEMENT- CAN ALSO REMOVE STOCK FROM THE STOCKLIST
            else:
                 #it existed and now we need the timestamps
                 filt_list_temp=map(lambda x:(x.split(',')[1]),filt_list_temp)
                 
                 
#                 for item in filt_list_temp:
#                     item= time.mktime(time.strptime(item,'%Y%m%d'))
#                     print item
                 
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
        
        print "No. of timestamps: " + str(len(tslist))
        
        for ts in tslist:
#            print str(ts)
            row= table.row
            row['timestamp']= ts
            row.append()
            #for ts in tslist ends
            
        table.flush()
        h5f.close()    
        
        print "makeTimestampsFile done"+ str(time.strftime("%H:%M:%S"))
        #makeTimestampsFile ends
        
    def continueChecking(self, tsList, beginTS, endTS):
        
#        print "In continueChecking"
        index=1
        DAY=86400
        
#        print "len(tsList): " + str(len(tsList))
        while (index < len(tsList)):
#            print "in the while loop " +str(int(tsList[index]))+"  "+str( int(tsList[index -1])) 
            if (int(tsList[index])- int(tsList[index -1]) > DAY):
                tempTS= tsList[index-1] + DAY
#                print "Found a gap..."
                while (tempTS< tsList[index]):
                    timeStruct= time.gmtime(tempTS)
#                    print "No stock traded on " + str (timeStruct[2])+"  "+str(timeStruct[1])+"  "+str(timeStruct[0])+" which is a " + str(timeStruct[6])
                    if not ((timeStruct[6] == 5) or (timeStruct[6] == 6)):
#                        print "Keep looking.."
                        return True #if its not a Saturday or a Sunday then keep looking
                        # if its not a Saturday or a Sunday
                        #Now check if this is christmas or something like that
                        
#                        if (len(tsList)> 366*2):
#                            #We have data for atleast 2 years, so lets lookup what happened in the last 2 years..
#                            try:
#                                tempTS.index (time.mktime(time.strptime(str(timeStruct[0]-1)+str(timeStruct[1])+str(timeStruct[2]),'%Y%m%d')))
#                                return True #continue checking because there seem to have been trades on the same day last year
#                             
#                            except:
#                                 try:
#                                    tempTS.index (time.mktime(time.strptime(str(timeStruct[0]-2)+str(timeStruct[1])+str(timeStruct[2]),'%Y%m%d'))) 
#                                 except:
#                                     # no trades for the last two years on this day
#                                     tempTS+=DAY
#                                     continue                             
                    tempTS+=DAY
                    #while (tempTS< tsList[index]) ends
            index+=1        
            #while ends
#        print "While loop done"
        #Checking from beginTS to start of list
        tempTS=time.mktime(time.strptime(str(beginTS),'%Y%m%d'))
        
        while (int(tsList[0])- int(tempTS) > DAY):
            timeStruct= time.gmtime((tempTS))
            if not ((timeStruct[6] == 5) or (timeStruct[6] == 6)):
#                print "beginTS keep looking"
                return True
                #if not... ends    
            tempTS+=DAY
            #while (tsList[0]- tempTS > DAY) ends
        
        
        #Checking from endTS to end of list
        tempTS=time.mktime(time.strptime(str(endTS),'%Y%m%d'))
        
        while (int(tempTS)- int(tsList[len(tsList)-1]) > DAY):
            timeStruct= time.gmtime(tempTS)
            if not ((timeStruct[6] == 5) or (timeStruct[6] == 6)):
#                print "endTS keep looking"
                return True
                #if not... ends    
            tempTS+=DAY
            #while (tempTS- tsList[len(tsList)-1] > DAY) ends
        
        print "Smartly figured out that we don't need to continue"
        return False #stop looking for more timestamps because all the timestamps that can be in the list are now there..
                     #we will not get any more timestamps by looking for more..because there just aren't any left... cool huh?    
#        print "continueChecking done"
        #continueChecking ends    
        
        
    def readTimestampsFromFile(self, fileName, beginTS, endTS):
        print "In readTimestampsFromFile " + str(time.strftime("%H:%M:%S"))
        h5f = pt.openFile(str(fileName), mode = "a")
        fileIterator= h5f.root.timestamps.timestamps
        
        tslist=[]
        for row in fileIterator.iterrows():
            temp= str(time.strftime("%Y%m%d", time.gmtime(row['timestamp'])))
            
            if (temp>= str(beginTS)) and (temp <= str(endTS)):
              tslist.append(temp)
              
            if (temp > str(endTS)):
                break
#            tslist.append(str(time.mktime(time.strptime(str(row['timestamp']),'%Y%m%d'))))
            
        h5f.close()
        
#        for item in tslist:
#            print item
            
        self.timestamps=tslist
        print "readTimestampsFromFile done " + str(time.strftime("%H:%M:%S"))
        #readTimestampsFromFile ends
        
#        return tslist    
        #readTimestampsFromFile
        
         
if __name__ == "__main__":
    
    print "starting..."+ str(time.strftime("%H:%M:%S"))
    #Folder that contains the stock data (1 file per stock)
    stockDataFolder = 'C:\\fin\\tempstocks'#'C:\\all stocks snapshot' #'C:\\all stocks snapshot' #'C:\\tempstocks'
    #File that contains the list of tickers to use (1 ticker per line)
    stocksToUseFile = 'C:\\fin\\stocks\\Lists\\NASDAQ_trial.txt' #NOT USED ANYMORE, Just some random string now...
    #Date to start reading data Format: YYYYMMDD
    startDate = 19840101
    #Date to end reading data Format: YYYYMMDD
    endDate = 19850109
    #Would you like to output an array (True) file or pytables (False) file
    isArray = False
    #Name of the file containing array information. Remember the '\\' at the end...
    outputFileFolder = 'C:\\fin\\tempoutput\\' #'C:\\tempoutput\\'#'C:\\generated data files\\one stock per file\\reading timestamps from a file 1\\'
    #The complete path to the file containing the list of timestamps
    timestampsFile="C:\\fin\\tempoutput\\timestamps.h5"    
   
    
    spd = StockPriceData(stockDataFolder)
#    spd.getSymbols()
#    spd.getMySymbols(stocksToUseFile)
    stocks = spd.getStocksList(stocksToUseFile)
    if(endDate<startDate):
        print "Error: enddate earlier than startdate"
        sys.exit(0)
        
    spd.makeOrUpdateTimestampsFile(timestampsFile, stocks, startDate, endDate)
    spd.readTimestampsFromFile(timestampsFile, startDate, endDate) 
    spd.getData(stocks, startDate, endDate, outputFileFolder)
    print "Tables File Generated. All Done"