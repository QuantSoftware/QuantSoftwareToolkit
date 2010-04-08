import dircache, pickle, time
from sets import Set
from numpy import NaN
import numpy as np
value = NaN


class StockPriceData:
    def __init__(self,dirname):
        self.dirname=dirname
        self.list_user_file_names = []
        self.filt_list=[]

#used to get the symbols from the allcsv directory
    def getSymbols(self): 
        list_file_names=dircache.listdir(self.dirname)
        list_file_names_strip_txt = map(lambda x:(x.split('.')[0]),list_file_names)
        return list_file_names
       # print list_file_names_strip_txt


# to get the user specified symbols       
    def getUserSymbols(self,filename): #used to get the 
        f=open(filename)
        list_user_tickers=f.readlines()
        f.close()
        for i in range(0,len(list_user_tickers)):
            list_user_tickers[i]=list_user_tickers[i].strip()
            #stocks_list.append(list_user_tickers[i].upper())
            list_user_tickers[i]=str(list_user_tickers[i]).upper()+".TXT"
       # print "user_tickers" + str(list_user_tickers)
        return list_user_tickers

# to find intersection of user specified symbols and allsymbols to leave out type etc
    def getMySymbols(self,filename):
        a=Set(self.getSymbols())
        b=Set(self.getUserSymbols(filename))
        c=a.intersection(b)
        list_user_file_names=list(c)
        list_user_file_names.sort()
        self.list_user_file_names = list_user_file_names
        list_user_file_names_strip_txt = map(lambda x:(x.split('.')[0]),list_user_file_names)
        #print "strip_txt" + str(list_user_file_names_strip_txt)
        return self.list_user_file_names

#get the stock list
    def getStocksList(self,filename):
        sym=self.getMySymbols(filename)
        stocks_list = []
        stocks_list = map(lambda x:(x.split('.')[0]),sym)
       # print "stocks_list" + str(stocks_list)
        return stocks_list

    
#get the time stamp
    def getTimeStamp(self):
        self.constructFilteredList()
        date_sorted = []
        for i in range(0,len(self.filt_list)):
            date_sorted.append(int(self.filt_list[i][0][1]))

        for i in range(0,len(date_sorted)):
            if(min(date_sorted)==date_sorted[i]):
                csv_date = i
                break
        timestamp_list = []
        for i in range(0,len(self.filt_list[csv_date])):
            temp=[]
            dateformat = self.filt_list[csv_date][i][1]
            parseddate = time.strptime(dateformat, '%Y%m%d')
            correctstamp = time.mktime(parseddate)
            temp.append(correctstamp)
            timestamp_list.append(temp)        
        #print timestamp_list
        #print map(lambda x: x[0],timestamp_list)
        #return timestamp_list
        return map(lambda x: x[0],timestamp_list)
        
# get an intermediate list (which is required by all classes-to make the extraction faster)           
    def constructFilteredList(self):
        i=0
        user_file_names_extract_data=self.list_user_file_names
               
        
        for x in user_file_names_extract_data:
            f=open(str(self.dirname)+"/"+str(x))
            j=f.readlines()
            f.close()
            j=j[1:-1]
            filt_list_temp=filter(lambda x: int(x.split(',')[1])>20030101,j)
            filt_list_temp=map(lambda x:(x.split(',')[0],x.split(',')[1],x.split(',')[2],x.split(',')[3],x.split(',')[4],x.split(',')[5],x.split(',')[6],(x.split(',')[7]).strip()),filt_list_temp)
            self.filt_list.append(filt_list_temp)
        #print filt_list[0][0]
        return self.filt_list





class StratDataFile:
    def __init__(self,timestamp_list, stocks_list):
        pass
        self.timestamps = np.array(timestamp_list)
        self.stocks = np.array(stocks_list)
        self.priceArray = np.ndarray( shape=(self.timestamps.size, self.stocks.size), dtype=np.object)


# get the data in array format
    def getData(self):
            
        
        for i in range(self.stocks.size):
            # print stocks[i]
            k = 0
            for j in range(self.timestamps.size):
            #   print str(timestamps[j]) +" <= "+ str(filt_list[i][k][1]) +" "+ str(i) +" "+ str(j) +  " "+ str(k)
                if(self.timestamps[j]<filt_list[i][k][1]):
            #        print str(timestamps[j]) +" < "+ str(filt_list[i][k][1]) +" "+ str(i) +" "+ str(j) +  " "+ str(k)
                    row = {}
                    row['exchange'] = 'NYSE'
                    row['symbol'] = self.stocks[i]
                    row['adj_open'] = NaN 
                    row['adj_close'] = NaN
                    row['adj_high'] = NaN
                    row['adj_low'] = NaN
                    row['close'] = NaN
                    row['volume'] = NaN
                    row['timestamp'] = self.timestamps[j]
                    row['when_available'] = self.timestamps[j]
                    row['interval'] = 86400
                    self.priceArray[j,i] = row
                elif(self.timestamps[j]==filt_list[i][k][1]):
             #       print str(timestamps[j]) +" == "+ str(filt_list[i][k][1]) +" "+ str(i) +" "+ str(j) +  " "+ str(k)
                    row = {}
                    row['exchange'] = 'NASDAQ'
                    row['symbol'] = self.stocks[i]
                    row['adj_open'] = filt_list[i][k][2] 
                    row['adj_close'] = filt_list[i][k][5]
                    row['adj_high'] = filt_list[i][k][3]
                    row['adj_low'] = filt_list[i][k][4]
                    row['close'] = filt_list[i][k][7]
                    row['volume'] = filt_list[i][k][6]
                    row['timestamp'] = self.timestamps[j]
                    row['when_available'] = self.timestamps[j]
                    row['interval'] = 86400
                    self.priceArray[j,i] = row
                    k=k+1
                #j=j+1

                
if __name__ == "__main__":
    spd = StockPriceData('C:/Users/Micah/Desktop/PBMS outputs/csvdata/allcsv') # replace with the proper directory
    spd.getSymbols()
    spd.getMySymbols('C:/Users/Micah/Desktop/PBMS outputs/csvdata/tickerlist_temp.txt') # replace with the proper file name
    stocks_list = spd.getStocksList('C:/Users/Micah/Desktop/PBMS outputs/csvdata/tickerlist_temp.txt') # replace with the proper file name
    timestamp_list = spd.getTimeStamp()
    #print timestamp_list
    filt_list = spd.constructFilteredList()



    sdf = StratDataFile(timestamp_list, stocks_list)
    sdf.getData()
    print sdf.timestamps[0], sdf.timestamps[sdf.timestamps.size-1]
    #print(sdf.priceArray[len(sdf.timestamps)-1][len(sdf.stocks)-1])
    #print sdf.priceArray
    pickle_output = open('defaultArrayFile.pkl','w')
    pickler = pickle.dump(sdf.timestamps,pickle_output)
    pickler = pickle.dump(sdf.stocks,pickle_output)
    pickler = pickle.dump(sdf.priceArray,pickle_output)
    pickle_output.close()
    print sdf.priceArray
    '''
    print 'between'
    pickle_output = open('defaultArrayFile.pkl','r')
    ts = pickle.load(pickle_output)
    st = pickle.load(pickle_output)
    pA = pickle.load(pickle_output)
    pickle_output.close()
    print 'after'
    '''
    #pickle_output = open('output.pkl','wb')
    #pickler = cPickle.dump(sdf,pickle_output)
    #pickle_output.close()


