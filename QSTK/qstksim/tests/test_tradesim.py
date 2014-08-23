'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on May 14, 2012

@author: Sourabh Bajaj
@contact: sourabh@sourabhbajaj.com
@summary: Test cases for tradeSim
'''

# Python imports
import datetime as dt
import unittest

# 3rd Party Imports
import pandas as pand
import numpy as np

# QSTK imports
import QSTK.qstksim


class Test(unittest.TestCase):
    df_close = None
    df_alloc = None
    i_open_result = None

    def _generate_data(self):
        
        ldt_timestamps = []
        na_close = np.ones( (16, 3) )

        for i in range(8):
            ldt_timestamps.append( dt.datetime(2012, 3, i+1, 9) )
            ldt_timestamps.append( dt.datetime(2012, 3, i+1, 16) )

        for i in range(16):
            if i == 0:
                na_close[i, :] = 1
            else:
                na_close[i, 0] = na_close[i-1, 0]+1
                na_close[i, 1] = na_close[i-1, 1]-0.02
			
                if (i % 3 == 0):
                    na_close[i, 2] = na_close[i-1, 2] + 0.2
                else:
                    na_close[i, 2] = na_close[i-1, 2]

        self.df_close = pand.DataFrame( index = ldt_timestamps, \
                        data = na_close, columns = ['A', 'B', 'C'] )

        # Create first allocation
        na_alloc = np.array( [[1, 0, 0], [0.5, 0.5, 0], [1.0, -1, 0], \
                       [1.0, 0, 1], [1.0, 0, 1], [.5, .5, 0], [0, .5, 0.5]] )

        ldt_timestamps = [dt.datetime( 2012, 3, 2, 13 )]
        ldt_timestamps.append( dt.datetime( 2012, 3, 3, 13 )  )
        ldt_timestamps.append( dt.datetime( 2012, 3, 3, 20 )  )
        ldt_timestamps.append( dt.datetime( 2012, 3, 4, 20 )  )
        ldt_timestamps.append( dt.datetime( 2012, 3, 5, 13 )  )
        ldt_timestamps.append( dt.datetime( 2012, 3, 6, 13 )  )
        ldt_timestamps.append( dt.datetime( 2012, 3, 8, 4 )  )

        self.df_alloc = pand.DataFrame( index=ldt_timestamps, \
                        data=na_alloc, columns=['A', 'B', 'C'] )
        self.df_alloc['_CASH'] = 0.0

        #Based on hand calculation using the transaction costs and slippage.
        self.i_open_result = 1.35011891

    def setUp(self):
        ''' Unittest setup function '''
        self._generate_data()

    def test_buy_close(self):
        ''' Tests tradesim buy-on-open functionality '''
        (df_funds, ts_leverage, f_commision, f_slippage, f_borrow) = \
              qstksim.tradesim( self.df_alloc, self.df_close, 10000, 1, True, 0.02,
                           5, 0.02 )

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

