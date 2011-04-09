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
    
    data_access= da.DataAccess('norgate')
    symbol_list= data_access.get_all_symbols()
    data_path= "/nethome/sjoshi42/temp/yhoo_trial/"
    
    _now =datetime.datetime.now();
    for symbol in symbol_list:
        print "Getting " + str (symbol)
        
        try:
            params= urllib.urlencode ({'a':03, 'b':12, 'c':2000, 'd':_now.month, 'e':_now.day, 'f':_now.year, 's': str(symbol)})
            url_get= urllib2.urlopen("http://ichart.finance.yahoo.com/table.csv?%s" % params)
            
            f= open (data_path + symbol + ".csv", 'w')
            f.write (url_get.read())
            f.close()
                        
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