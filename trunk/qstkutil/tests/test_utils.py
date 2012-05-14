'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on May 14, 2012

@author: John Cornwell
@contact:  John@lucenaresearch.com
@summary: 

'''

# Python imports
import unittest

# 3rd party imports

# QSTK imports



class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def test_import(self):
        # Silly example to test current error in loading utils
        import qstkutil.utils as utils
        self.assertTrue(True)
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()