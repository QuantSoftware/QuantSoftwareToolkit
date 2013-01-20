#
# report.py
#
# Generates a html file containing a report based 
# off a timeseries of funds from a pickle file.
#
# Drew Bratcher
#

from pylab import *
import numpy
from QSTK.qstkutil import DataAccess as da
from QSTK.qstkutil import qsdateutil as du
from QSTK.qstkutil import tsutil as tsu
from QSTK.quicksim import quickSim as qs
import converter
import datetime as dt
from pandas import *
import matplotlib.pyplot as plt
import cPickle

def readableDate(date):
	return str(date.month)+"/"+str(date.day)+"/"+str(date.year)

def getYearReturn(funds, year):
	days=[]
	for date in funds.index:
		if(date.year==year):
			days.append(date)
	return funds[days[-1]]/funds[days[0]]-1

def getYearMaxDrop(funds, year):
	days=[]
	for date in funds.index:
		if(date.year==year):
			days.append(date)
	maxdrop=0
	prevday=days[0]
	for day in days[1:-1]:
		if((funds[day]/funds[prevday]-1)<maxdrop):
			maxdrop=funds[day]/funds[prevday]-1
		prevday=day
	return maxdrop

def getYearRatioUsingMonth(funds,year):
	days=[]
	for date in funds.index:
		if(date.year==year):
			days.append(date)
	funds=funds.reindex(index=days)
	m=tsu.monthly(funds)
	avg=float(sum(m))/len(m)
	std=0
	for a in m:
		std=std+float((float(a-avg))**2)
	std=sqrt(float(std)/(len(m)-1))
	return (avg/std)

def getWinningDays(funds1,funds2,year):
	days=[]
	i=0;
	win=0
	tot=0
	f1ret=tsu.daily(funds1)
	f2ret=tsu.daily(funds2)
	relf1=[]
	relf2=[]
	for date in funds1.index:
		if(date.year==year):
			for date2 in funds2.index:
				if(date==date2):
					relf1.append(f1ret[i])
					relf2.append(f2ret[i])
		i+=1
	
	for i in range(0,len(relf1)):
		if(f1ret[i]>f2ret[i]):
			win+=1
		tot+=1
	return float(win)/tot

def runOther(funds,symbols):
	tsstart =dt.datetime(funds.index[0].year,funds.index[0].month,funds.index[0].day)
	tsend =dt.datetime(funds.index[-1].year,funds.index[-1].month,funds.index[-1].day)
	timeofday=dt.timedelta(hours=16)
	timestamps=du.getNYSEdays(tsstart,tsend,timeofday)
	dataobj=da.DataAccess('Norgate')
	historic=dataobj.get_data(timestamps,symbols,"close")
	alloc_val=float(0.1/(float(len(symbols))+1))
	alloc_vals=alloc_val*ones(len(symbols))
	alloc=DataMatrix(index=[historic.index[0]],data=[alloc_vals], columns=symbols)
	alloc=alloc.append(DataMatrix(index=[historic.index[-1]], data=[alloc_vals], columns=symbols))
	alloc['_CASH']=alloc_val
	return qs.quickSim(alloc,historic,1000)

def reportFunctionality(funds, symbols,filename=sys.stdout):
	if(len(symbols)!=0):
		funds2=runOther(funds,symbols)
		arg2=1
	else:
		arg2=0

	if(filename==sys.stdout):
		html_file=sys.stdout
	else:
		html_file = open(filename,"w")
	
	#top
	html_file.write("<HTML>\n")
	html_file.write("<HEAD>\n")	
	html_file.write("<TITLE>QSTK Generated Report from "+readableDate(funds.index[0])+" to "+readableDate(funds.index[-1])+"</TITLE>\n")
	html_file.write("</HEAD>\n\n")
	html_file.write("<BODY><CENTER>\n\n")
	
	years=du.getYears(funds)

	html_file.write("<H2>Performance Summary for "+sys.argv[1]+"</H2>\n")
	html_file.write("For the dates "+readableDate(funds.index[0])+" to "+readableDate(funds.index[-1])+"\n")


	html_file.write("<H3>Yearly Performance Metrics</H3>\n")


	html_file.write("<TABLE CELLPADDING=10>\n")
	html_file.write("<TR><TH></TH>\n")
	for year in years:
		html_file.write("<TH>"+str(year)+"</TH>\n")
	html_file.write("</TR>\n")

	#yearly return
	html_file.write("<TR>\n")
	html_file.write("<TH>Annualized Return:</TH>\n")
	for year in years:
		retur=getYearReturn(funds,year)
		html_file.write("<TD>\n")
		print >>html_file, "%.2f\n" % (retur*100) 
		html_file.write("%</TD>\n")
	html_file.write("</TR>\n")

	#yearly winning days
	html_file.write("<TR>\n")
	html_file.write("<TH>Winning Days:</TH>\n")
	for year in years:
		# change to compare to inputs - ratio=tsu.getYearRatio(funds,year)
		if(arg2!=0):
			win=getWinningDays(funds,funds2,year)
			html_file.write("<TD>\n")
			print >>html_file, "%.2f\n" % (win*100)
			html_file.write("%</TD>\n")
		else:
			html_file.write("<TD>No comparison.</TD>\n")
	html_file.write("</TR>\n")

	#max draw down
	html_file.write("<TR>\n")
	html_file.write("<TH>Max Draw Down:</TH>\n")
	for year in years:
		drop=getYearMaxDrop(funds,year)
		html_file.write("<TD>\n")
		print >>html_file, "%.2f" % (drop*100)
		html_file.write("%</TD>\n")
	html_file.write("</TR>\n")

	#yearly sharpe ratio using daily rets
	html_file.write("<TR>\n")
	html_file.write("<TH>Daily Sharpe Ratio:</TH>\n")
	for year in years:
		ratio=tsu.getYearRatio(funds,year)
		html_file.write("<TD>\n")
		print >>html_file, "%.2f\n" % ratio
		html_file.write("</TD>\n")
	html_file.write("</TR>\n")


	#yearly sharpe ratio using monthly rets
	html_file.write("<TR>\n")
	html_file.write("<TH>Monthly Sharpe Ratio:</TH>\n")
	for year in years:
		ratio=getYearRatioUsingMonth(funds,year)
		html_file.write("<TD>\n")
		print >>html_file, "%.2f\n" % ratio
		html_file.write("</TD>\n")
	html_file.write("</TR>\n")
	
	html_file.write("</TABLE>\n")
	html_file.write("<BR/>\n\n")

	vals=funds.values;
	vals2=np.append(vals,funds2.values,2)


	df=DataMatrix(index=funds.index,data=funds.values, columns=['fund'])
	df2=DataMatrix(index=funds2.index,data=funds2.values,columns=['other'])
	df['other']=df2['other']

	corrcoef=numpy.corrcoef(funds.values[0:-1],funds2.values)
	html_file.write("<H3>Correlation=")
	print >>html_file, "%.2f\n" % corrcoef[0][1]
	html_file.write("<H3>\n")
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

	i=0
	for year in years:
		html_file.write("<TR>\n")
		html_file.write("<TH>"+str(year)+"</TH>\n")
		months=du.getMonths(funds,year)
		for month in months:
			html_file.write("<TD>\n")
			print >>html_file, "%.2f\n" % (mrets[i]*100)
			html_file.write("%</TD>\n")
			i+=1
		html_file.write("</TR>\n")
	html_file.write("</TABLE>\n")
	html_file.write("<BR/>\n\n")

	#fund value graph
	fundlist=[];
	fundlist.append(funds)
	fundlist.append(funds2)
	converter.fundsToPNG(fundlist,'funds.png')
	html_file.write("<IMG SRC=\'./funds.png\'/>\n")
	html_file.write("<BR/>\n\n")
	
	#end
	html_file.write("</CENTER></BODY>\n\n")
	html_file.write("</HTML>")



if __name__ == '__main__':
	input=open(sys.argv[1],"r")
	funds=cPickle.load(input)

	if(len(sys.argv)>2):
		input2=sys.argv[2]
		symbols=sys.argv[2].split(',')
		reportFunctionality(funds,symbols,'investors_report.html')
	else:
		reportFunctionality(funds,0,'investors_report.html')
