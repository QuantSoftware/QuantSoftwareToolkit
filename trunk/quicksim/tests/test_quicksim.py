'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on Mar 20, 2012

@author: John Cornwell
@contact: JWCornV@gmail.com
@summary: Test cases for quicksim package
'''

# Python imports
import datetime as dt
import unittest

# 3rd Party Imports
import pandas as pand
import numpy as np

# QSTK imports
from quicksim import quickSim as qs



class Test(unittest.TestCase):
    ''' Test Class '''
    
    df_close = None
    df_alloc = None
    i_open_result = None

    def _generate_data(self):
        ''' Generate canned data '''
        
        ldt_timestamps = []
        
        na_close = np.ones( (12, 3) )
        #na_open = np.ones( (12, 3) ) * np.NAN
    
        # Three fake stocks, first one doubles, second one triples, third one 
        # halves.  The open price the next day looses half of the juice, i.e. 
        # midpoint between closes.
        for i in range(12):
            if i == 0:
                pass
            else:
                na_close[i, 0] =  na_close[i-1, 0] * 2.0
                na_close[i, 1] =  na_close[i-1, 1] * 3.0
                na_close[i, 2] =  na_close[i-1, 2] * 0.5
                
#                # Leave first open price 0
#                if i > 1:
#                    for unused in range(3):
#                        pass
#                        # TODO get open values 
#                        #na_close[i,0] =  na_close[i-1,0] * 2.0
    
                
            ldt_timestamps.append( dt.datetime(2012, 3, i+1) )
        
        self.df_close = pand.DataMatrix( index=ldt_timestamps, data=na_close,
                                         columns=['A','B','C'] )
        
        # Create first allocation
        na_alloc = np.array( [[1, 0, 0], [0, 1, 0], [0, 0, 1], [.5, .5, 0], [0, 0, 0]] )
        
        ldt_timestamps = [dt.datetime( 2012, 3, 4 )]
        ldt_timestamps.append( dt.datetime( 2012, 3, 6 )  )
        ldt_timestamps.append( dt.datetime( 2012, 3, 8 )  )
        ldt_timestamps.append( dt.datetime( 2012, 3, 9 )  )
        ldt_timestamps.append( dt.datetime( 2012, 3, 10 )  )
        
        # The above doubles your money on march 4,5, triples, on 6,7th, halves
        # on 8th, 1/2 doubles 1/2 triples on the 9th. 
        # 2 * 2 * 3 * 3 * 1/2 * (.5*2 +.5*3) = 45
        self.i_open_result = 45
        
        self.df_alloc = pand.DataMatrix( index=ldt_timestamps, data=na_alloc,
                                         columns=['A','B','C'] )
        self.df_alloc['_CASH'] = 0.0

    def setUp(self):
        ''' Unittest setup function '''
        self._generate_data()

    def test_buy_close(self):
        ''' Tests quicksim buy-on-open functionality '''
        df_funds = qs.quickSim( self.df_alloc, self.df_close, 100 )
        self.assertTrue( df_funds[-1] == 100 * self.i_open_result )


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()

