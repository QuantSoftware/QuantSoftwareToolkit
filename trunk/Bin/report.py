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
from qstkutil import dateutil as du
from qstkutil import tsutil as tsu
from quicksim import quickSim as qs
from Bin import converter

from pandas import *
import matplotlib.pyplot as plt
import cPickle

print sys.argv[1]
input=open(sys.argv[1],"r")
funds=cPickle.load(input)

filename = "report.html"
html_file = open(filename,"w")

#top
html_file.write("<HTML>\n")
html_file.write("<HEAD>\n")
html_file.write("<TITLE>QSTK Generated Report:"+str(sys.argv[1])+"</TITLE>\n")
html_file.write("</HEAD>\n\n")
html_file.write("<BODY><CENTER>\n\n")

#fund value graph
converter.fundsToPNG(funds,'funds.png')
html_file.write("<H2>QSTK Generated Report:"+str(sys.argv[1])+"</H2>\n")
html_file.write("<IMG SRC=\'./funds.png\'/>\n")
html_file.write("<BR/>\n\n")

#montly returns
mrets=tsu.monthly(funds)
html_file.write("<H2>Monthly Returns</H2>\n")
html_file.write("<TABLE CELLPADDING=10>\n")
html_file.write("<TR>\n")
html_file.write("<TH></TH>\n")
month_names=du.getMonthNames()
for name in month_names:
	html_file.write("<TH>"+str(name)+"</TH>\n")
html_file.write("</TR>\n")
years=du.getYears(funds)
i=0
for year in years:
	html_file.write("<TR>\n")
	html_file.write("<TH>"+str(year)+"</TH>\n")
	months=du.getMonths(funds,year)
	for month in months:
		html_file.write("<TD>"+str(mrets[i]*100)[:4]+"%</TD>\n")
		i+=1
	html_file.write("</TR>\n")
html_file.write("</TABLE>\n")
html_file.write("<BR/>\n\n")

#sharpe ratio
ratio=tsu.getRatio(funds)
html_file.write("<H3>Overall Sharpe Ratio: "+str(ratio)+"</H3>\n")
html_file.write("<TABLE CELLPADDING=10>\n")
html_file.write("<TR><TH></TH>\n")
for year in years:
	html_file.write("<TH>"+str(year)+"</TH>\n")
html_file.write("</TR>\n")
html_file.write("<TR>\n")
html_file.write("<TH>Sharpe Ratio:</TH>\n")
for year in years:
	ratio=tsu.getYearRatio(funds,year)
	html_file.write("<TD>"+str(ratio)+"</TD>\n")
html_file.write("</TR>\n")
html_file.write("</TABLE>\n")
html_file.write("<BR/>\n\n")

#end
html_file.write("</CENTER></BODY>\n\n")
html_file.write("</HTML>")

