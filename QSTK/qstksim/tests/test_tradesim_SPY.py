'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on May 19, 2012

@author: Sourabh Bajaj
@contact: sourabh@sourabhbajaj.com
@summary: Test cases for tradeSim - Monthly Rebalancing of $SPX
'''

# Python imports
import datetime as dt
import unittest

# 3rd Party Imports
import pandas as pand
import numpy as np

# QSTK imports
import QSTK.qstksim
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.qsdateutil as du


class Test(unittest.TestCase):
    df_close = None
    df_alloc = None
    i_open_result = None

    def _generate_data(self):

        year = 2009        
        startday = dt.datetime(year-1, 12, 1)
        endday = dt.datetime(year+1, 1, 31)

        l_symbols = ['$SPX']

        #Get desired timestamps
        timeofday = dt.timedelta(hours = 16)
        ldt_timestamps = du.getNYSEdays(startday, endday, timeofday)

        dataobj = da.DataAccess('Norgate')
        self.df_close = dataobj.get_data( \
                        ldt_timestamps, l_symbols, "close", verbose=True)

        self.df_alloc = pand.DataFrame( \
                        index=[dt.datetime(year, 1, 1)], \
                                data=[1], columns=l_symbols)

        for i in range(11):
            self.df_alloc = self.df_alloc.append( \
                     pand.DataFrame(index=[dt.datetime(year, i+2, 1)], \
                                      data=[1], columns=l_symbols))

        self.df_alloc['_CASH'] = 0.0

        #Based on hand calculation using the transaction costs and slippage.
        self.i_open_result = 1.15921341122
	

    def setUp(self):
        ''' Unittest setup function '''
        self._generate_data()

    def test_buy_close(self):
        ''' Tests tradesim buy-on-open functionality '''
        (df_funds, ts_leverage, f_commision, f_slippage, f_borrow) = \
              qstksim.tradesim( self.df_alloc, self.df_close, 10000, 1, True, 0.02,
                           5, 0.02)

        print 'Commision Costs : ' + str(f_commision)
        print 'Slippage : ' + str(f_slippage)
        print 'Short Borrowing Cost : ' + str(f_borrow)
        print 'Leverage : '	
        print ts_leverage
        np.testing.assert_approx_equal(df_funds[-1], \
             10000 * self.i_open_result, significant = 3)
        self.assertTrue(True)
        #self.assertTrue(abs(df_funds[-1] - 10000 * self.i_open_result)<=0.01)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()

