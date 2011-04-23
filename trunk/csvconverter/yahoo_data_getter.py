'''
Created on Apr 8, 2011

@author: sjoshi42
@summary: This modules get stock data from yahoo finance
'''

import qstkutil.DataAccess as da
import qstkutil.utils as utils
import urllib2
import urllib
import datetime
import sys
import os

def main():
    #Getting path
    path= os.environ['QSDATA']
    
    get_data_for_exchange("NASDAQ", path)
    get_data_for_exchange("NYSE", path)
    get_data_for_exchange("AMEX", path)
    
    #main ends
def get_data_for_exchange (exchange, data_path):
    
    #data_access= da.DataAccess('norgate')
    #symbol_list= data_access.get_all_symbols()
    data_path= data_path + "/Raw/Yahoo/US/" + str (exchange) + "/"
    
    #Create path if it doesn't exist
    if not (os.access(data_path, os.F_OK)):
        os.makedirs(data_path)
        
    utils.clean_paths(data_path)    
    
    symbol_list= list()
    
    print "Getting list of stocks.."
    
    try:
        nasdaq_params= urllib.urlencode ({'exchange':str(exchange), 'render':'download'})
        nasdaq_get= urllib2.urlopen ('http://www.nasdaq.com/screening/companies-by-name.aspx?%s' % nasdaq_params)
        symbol_list.append (nasdaq_get.readline()) #Now we have all the data in a list- but we need only the symbols so we remove the rest
        while (len (symbol_list[-1]) > 0):
            symbol_list.append (nasdaq_get.readline())
            #while ends
        symbol_list.pop(0) #This is just the word "symbol" and not a symbol itself    
        symbol_list.pop(-1) #Remove the last element because its going to be blank anyway    
        #symbol_list = map(lambda x:(x.partition(str(","))[0]),symbol_list) #Get the stuff before the first comma- which is the symbol
        
        #Unfortunately this symbol is in quotes. So we have to remove them now
        symbol_list = map(lambda x:(x.partition(str("\""))[2]),symbol_list) #Keep the stuff only after the first "
        symbol_list = map(lambda x:(x.partition(str("\""))[0]),symbol_list) #Keep the stuff before the second "
        
        
    except urllib2.HTTPError:
        print "Unable to get list of stocks from server. Please check your internet connection and retry."
    except:
        print"Unknown error occoured when getting list of stocks from server."
    
    print "Got " + str (len(symbol_list)) + " symbols. Now getting symbol data..."
    
    _now =datetime.datetime.now();
    miss_ctr=0; #Counts how many symbols we could get
    
    for symbol in symbol_list:
        symbol_data=list()
        print "Getting " + str (symbol)
        
        try:
            params= urllib.urlencode ({'a':03, 'b':12, 'c':2000, 'd':_now.month, 'e':_now.day, 'f':_now.year, 's': str(symbol)})
            url_get= urllib2.urlopen("http://ichart.finance.yahoo.com/table.csv?%s" % params)
            
            header= url_get.readline()
            symbol_data.append (url_get.readline())
            while (len(symbol_data[-1]) > 0):
                symbol_data.append(url_get.readline())
#                print str(symbol_data[-1])
            
            symbol_data.pop(-1) #The last element is going to be the string of length zero. We don't want to write that to file.
            #Following changes so that the data looks like Norgate data and the change to cav_to_pkl.csv is minimized
            symbol_data = map(lambda x:(x.replace("-", "")),symbol_data) 
            symbol_data = map(lambda x:(str(symbol) + "," + str(x)) ,symbol_data) #This means that the header is wrong but since it is ignored later anyways- this will work 

            #now writing data to file
            f= open (data_path + symbol + ".csv", 'w')
            
            #Writing the header
            f.write (header)
            
            while (len(symbol_data) > 0):
                f.write (symbol_data.pop())
             
            f.close();    
#            print url_get.readline()
#            f= open (data_path + symbol + ".csv", 'w')
#            f.write (url_get.read())
#            f.close()
                        
        except urllib2.HTTPError:
            miss_ctr= miss_ctr+1
            print "Unable to fetch data for stock: " + str (symbol)
#        except:
#            print "Some error occurred"
            #except ends 
            
        
        #for ends
    print "All done. Got " + str (len(symbol_list) - miss_ctr) + " stocks. Could not get " + str (miss_ctr) + " stocks."   
    #main ends


if __name__ == '__main__':
    main()