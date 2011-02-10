#
# sharpratio.py
#
# Generates a html file containing a report based 
# off a timeseries of funds from a pickle file.
#
# Drew Bratcher
#

from pylab import *
from qstkutil import DataAccess as da
from qstkutil import timeutil as tu
from qstkutil import pseries as ps
from pandas import *
import quickSim as simulator
import matplotlib.pyplot as plt

#calculate average annual rate of return
#calculate average annual return standard deviation
#use input value for available rate of return for risk free security
# use formula S(x)=(avg - riskfree)/stddev(x) 

