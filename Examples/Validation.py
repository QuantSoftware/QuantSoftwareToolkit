'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on February, 9, 2013

@author: Sourabh Bajaj
@contact: sourabhbajaj@gatech.edu
@summary: Python Validation Script
'''

# Printing what Python Version is installed : QSTK uses 2.7
import sys
import platform
print "Python Details : "
print sys.version
print "Your Python Version is : ", platform.python_version()
print "QSTK uses Python 2.7.X (2.7.3 recommended and supported)"
print "Please make sure you're using the correct python version."
print

# Printing the directory you are in
import os
print "Current Directory : ", os.path.abspath('.')
print

# Printing files in the current directory.
print "Files in the current directory"
ls_files = os.listdir('.')
for s_file in ls_files:
    print s_file
print

# Testing the dependencies
# Testing numpy
try:
    import numpy
    print "Numpy is installed and the version used is : ", numpy.__version__
    print "Please make sure you're using version >= 1.6.1"
except ImportError:
    sys.exit("Error : Numpy can not be imported or not installed.")
print

# Testing matplotlib
try:
    import matplotlib
    print "Matplotlib is installed and version is : ", matplotlib.__version__
    print "Please make sure you're using version >= 1.1.0"
except ImportError:
    sys.exit("Error : Matplotlib can not be imported or not installed.")
print

# Testing Pandas
try:
    import pandas
    print "Pandas is installed and the version used is : ", pandas.__version__
    print "Please make sure you're using version >= 0.7.3"
except ImportError:
    sys.exit("Error : Pandas can not be imported or not installed.")
print


# Testing Scipy
try:
    import scipy
    print "Scipy is installed and the version used is : ", scipy.__version__
    print "Please make sure you're using version >= 0.9.0"
except ImportError:
    sys.exit("Error : Scipy can not be imported or not installed.")
print

# Testing Dateutil
try:
    import dateutil
    print "Dateutil is installed and the version used is : ", dateutil.__version__
    print "Please make sure you're using version == 1.5"
except ImportError:
    sys.exit("Error : Dateutil can not be imported or not installed.")
print

# Testing Setuptools
try:
    import setuptools
    print "Setuptools is installed and the version used is : ", setuptools.__version__
    print "Please make sure you're using version >= 0.6"
except ImportError:
    sys.exit("Error : Setuptools can not be imported or not installed.")
print

# # Testing CVXOPT
# try:
#     import cvxopt
#     print "CVXOPT is installed and can be imported"
# except ImportError:
#     sys.exit("Error : CVXOPT can not be imported or not installed.")
# print

# Testing datetime
try:
    import datetime as dt
    print "datetime is installed and can be imported"
except ImportError:
    sys.exit("Error : datetime can not be imported or not installed.")
print

# All dependencies are installed and working
print "All dependencies are installed and working\n"

# Testing import of QSTK
# Testing QSTK
try:
    import QSTK
    print "QSTK is installed and can be imported"
except ImportError:
    sys.exit("Error : QSTK can not be imported or not installed.")
print

# Testing QSTK.qstkutil
try:
    import QSTK.qstkutil.tsutil as tsu
    import QSTK.qstkutil.qsdateutil as du
    import QSTK.qstkutil.DataAccess as da
    print "QSTK.qstkutil is installed and can be imported"
except ImportError:
    exit("Error : QSTK.qstkutil can not be imported.")
print

# Testing QSTK.qstkstudy
try:
    import QSTK.qstkstudy.EventProfiler
    print "QSTK.qstkstudy is installed and can be imported"
except ImportError:
    exit("Error : QSTK.qstkstudy can not be imported.")
print

# Checking that the data installed is correct.
# Start and End date of the charts
dt_start = dt.datetime(2012, 2, 10)
dt_end = dt.datetime(2012, 2, 24)
dt_timeofday = dt.timedelta(hours=16)

# Get a list of trading days between the start and the end.
ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)
ls_symbols = ['MSFT', 'GOOG']

# Creating an object of the dataaccess class with Yahoo as the source.
c_dataobj = da.DataAccess('Yahoo', verbose=True)
# Reading adjusted_close prices
df_close = c_dataobj.get_data(ldt_timestamps, ls_symbols, "close")
print df_close
print
print "\nCorrect Output using the Default Data should be : "
print "Assignments use this data for grading"
print "                      MSFT    GOOG"
print "2012-02-10 16:00:00  29.90  605.91"
print "2012-02-13 16:00:00  29.98  612.20"
print "2012-02-14 16:00:00  29.86  609.76"
print "2012-02-15 16:00:00  29.66  605.56"
print "2012-02-16 16:00:00  30.88  606.52"
print "2012-02-17 16:00:00  30.84  604.64"
print "2012-02-21 16:00:00  31.03  614.00"
print "2012-02-22 16:00:00  30.86  607.94"
print "2012-02-23 16:00:00  30.96  606.11"
print

dt_test = dt.datetime(2012, 2, 15, 16)
print "Close price of MSFT on 2012/2/15 is : ", df_close['MSFT'].ix[dt_test]
if df_close['MSFT'].ix[dt_test] == 29.66:
    print "Data looks correct as the close price in default data is 29.66"
else:
    print "Default data used in the assisgnments has close price as 29.66"
    sys.exit("Error : Data has changed so does not match data used in Assignments")
print

print "Everything works fine: You're all set."
