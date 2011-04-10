'''
Created on Apr 8, 2011

@author: sjoshi42
@summary: This modules get stock data from yahoo finance
'''

import qstkutil.DataAccess as da
import urllib2
import urllib
import datetime

def main ():
    
    #data_access= da.DataAccess('norgate')
    #symbol_list= data_access.get_all_symbols()
    data_path= "C:\\temp\\"
    symbol_list= list()
    symbol_list.append("AAPL")
    
    _now =datetime.datetime.now();
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
                print str(symbol_data[-1])
            
            symbol_data.pop() #The last element is going to be the string of length zero. We don't want to write that to file.
            #now writing data to file
            f= open (data_path + symbol + ".csv", 'w')
            
            #Writing the header
            f.write (header)
            while (len(symbol_data) > 1):
                f.write (symbol_data.pop())
             
            f.close();    
               
               
                           
#            print url_get.readline()
#            f= open (data_path + symbol + ".csv", 'w')
#            f.write (url_get.read())
#            f.close()
                        
        except urllib2.HTTPError:
            got_data= False;
            print "Unable to get data for stock: " + str (symbol)
        except:
            print "Some error occurred"
            #except ends 
            
        
          

            

        
        #for ends
    print "All done!"   
    #main ends


if __name__ == '__main__':
    main()