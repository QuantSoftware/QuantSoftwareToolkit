#
# report.py
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


os.system('python fundsToPNG.py '+str(sys.argv[1]))

filename = "report.html"
html_file = open(filename,"w")
html_file.writeline("<HTML>")
html_file.writeline("<HEAD>")
html_file.writeline("QSTK Report")
html_file.writeline("</HEAD>")
html_file.writeline("<BODY>")
html_file.writeline("<img src=fundToPNG/>")
html_file.writeline("<br>")
html_file.writeline("</BODY>")
html_file.writeline("</HTML>")

