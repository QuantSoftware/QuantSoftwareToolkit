'''
Pulling Yahoo CSV Data
'''

import urllib2
import urllib
import datetime
import os
import QSTK.qstkutil.DataAccess as da


def get_yahoo_data(data_path, ls_symbols):
    '''Read data from Yahoo
    @data_path : string for where to place the output files
    @ls_symbols: list of symbols to read from yahoo
    '''
    # Create path if it doesn't exist
    if not (os.access(data_path, os.F_OK)):
        os.makedirs(data_path)

    ls_missed_syms = []
    # utils.clean_paths(data_path)   

    _now = datetime.datetime.now()
    # Counts how many symbols we could not get
    miss_ctr = 0
    for symbol in ls_symbols:
        # Preserve original symbol since it might
        # get manipulated if it starts with a "$"
        symbol_name = symbol
        if symbol[0] == '$':
            symbol = '^' + symbol[1:]

        symbol_data = list()
        # print "Getting {0}".format(symbol)

        try:
            params = urllib.urlencode ({'a':0, 'b':1, 'c':2000, 'd':_now.month-1, 'e':_now.day, 'f':_now.year, 's': symbol})
            url = "http://ichart.finance.yahoo.com/table.csv?%s" % params
            url_get = urllib2.urlopen(url)
            
            header = url_get.readline()
            symbol_data.append (url_get.readline())
            while (len(symbol_data[-1]) > 0):
                symbol_data.append(url_get.readline())

            # The last element is going to be the string of length zero. 
            # We don't want to write that to file.
            symbol_data.pop(-1)
            #now writing data to file
            f = open (data_path + symbol_name + ".csv", 'w')

            #Writing the header
            f.write (header)

            while (len(symbol_data) > 0):
                f.write (symbol_data.pop(0))

            f.close()

        except urllib2.HTTPError:
            miss_ctr += 1
            ls_missed_syms.append(symbol_name)
            print "Unable to fetch data for stock: {0} at {1}".format(symbol_name, url)
        except urllib2.URLError:
            miss_ctr += 1
            ls_missed_syms.append(symbol_name)
            print "URL Error for stock: {0} at {1}".format(symbol_name, url)

    print "All done. Got {0} stocks. Could not get {1}".format(len(ls_symbols) - miss_ctr, miss_ctr)
    return ls_missed_syms


def read_symbols(s_symbols_file):
    '''Read a list of symbols'''
    ls_symbols = []
    ffile = open(s_symbols_file, 'r')
    for line in ffile.readlines():
        str_line = str(line)
        if str_line.strip(): 
            ls_symbols.append(str_line.strip())
    ffile.close()
    return ls_symbols 


def update_my_data():
    '''Update the data in the root dir'''
    c_dataobj = da.DataAccess('Yahoo', verbose=True)
    s_path = c_dataobj.rootdir
    ls_symbols = c_dataobj.get_all_symbols()
    ls_missed_syms = get_yahoo_data(s_path, ls_symbols)
    # Making a second call for symbols that failed to double check
    get_yahoo_data(s_path, ls_missed_syms)
    return


def main():
    '''Main Function'''
    path = './'
    ls_symbols = read_symbols('symbols.txt')
    get_yahoo_data(path, ls_symbols)

if __name__ == '__main__':
    main()
