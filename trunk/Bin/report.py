#
# report.py
#
# Generates a html file containing a report based 
# off a timeseries of funds from a pickle file.
#
# Drew Bratcher
#
from os import path
from pylab import *
from qstkutil import DataAccess as da
from qstkutil import dateutil as du
from qstkutil import tsutil as tsu
from quicksim import quickSim as qs
import converter

from pandas import *
import matplotlib.pyplot as plt
import cPickle
import datetime as dt

SPX_CLOSE=0

def print_header(html_file, name):
	#top
	html_file.write("<HTML>\n")
	html_file.write("<HEAD>\n")
	html_file.write("<TITLE>QSTK Generated Report:"+name+"</TITLE>\n")
	html_file.write("</HEAD>\n\n")
	html_file.write("<BODY><CENTER>\n\n")

def print_footer(html_file):
	html_file.write("</CENTER></BODY>\n\n")
	html_file.write("</HTML>")

def print_stats(funds, benchmark, name):
	start_date=funds.index[0].strftime("%m/%d/%Y")
	end_date=funds.index[-1].strftime("%m/%d/%Y")
	sys.stdout.write("</CENTER><PRE>\n")
	sys.stdout.write("Performance Summary for "+str(path.basename(name))+" Backtest (Long Only)\n")
	sys.stdout.write("For the dates "+str(start_date)+" to "+str(end_date)+"\n\n")
	sys.stdout.write("Yearly Performance Metrics \n")
	years=du.getYears(funds)
	sys.stdout.write("\n\t\t\t\t")
	for year in years:
		sys.stdout.write("\t"+str(year))
	sys.stdout.write("\n")
	sys.stdout.write("Fund Annualized Return:\t\t")
	for year in years:
		year_vals=[]
		for date in funds.index:
			if(date.year==year):
				year_vals.append(funds[date])
		day_rets=tsu.daily1(year_vals)
		ret=tsu.getRorAnnual(day_rets[1:-1])
		x="\t%2.2f%%" % (ret*100)
		sys.stdout.write(x)

	sys.stdout.write("\n$SPX Annualized Return:\t\t")
	timeofday=dt.timedelta(hours=16)
	timestamps=du.getNYSEdays(funds.index[0], funds.index[-1], timeofday)
	dataobj=da.DataAccess('Norgate')
	global SPX_CLOSE
	SPX_CLOSE=dataobj.get_data(timestamps,benchmark, "close", verbose=False)
	for year in years:
		year_vals=[]
		for date in SPX_CLOSE.index:
			if(date.year==year):
				year_vals.append(SPX_CLOSE.xs(date))
		day_rets=tsu.daily1(year_vals)
		ret=tsu.getRorAnnual(day_rets[1:-1])
		x="\t%2.2f%%" % (ret*100)
		sys.stdout.write(x)

	sys.stdout.write("\n\nFund Winning Days:\t\t")                
	for year in years:
		year_vals=[]
		for date in funds.index:
			if(date.year==year):
				year_vals.append(funds[date])
		ret=float(tsu.getWinning(year_vals))/float(len(year_vals))
		x="\t%+2.1f%%" % ret
		sys.stdout.write(x)

	sys.stdout.write("\n$SPX Winning Days:\t\t")                
	for year in years:
		year_vals=[]
		for date in SPX_CLOSE.index:
			if(date.year==year):
				year_vals.append(SPX_CLOSE.xs(date))
		ret=float(tsu.getWinning(year_vals))/float(len(year_vals))
		x="\t%+2.1f%%" % ret
		sys.stdout.write(x)

	sys.stdout.write("\n\nFund Max Draw Down:\t\t")
	for year in years:
		year_vals=[]
		for date in funds.index:
			if(date.year==year):
				year_vals.append(funds[date])
		ret=tsu.getDrawDown(year_vals)
		x="\t%+2.1f%%" % (ret*100)
		sys.stdout.write(x)

	sys.stdout.write("\n$SPX Max Draw Down:\t\t")
	for year in years:
		year_vals=[]
		for date in SPX_CLOSE.index:
			if(date.year==year):
				year_vals.append(SPX_CLOSE.xs(date))
		ret=tsu.getDrawDown(year_vals)
		x="\t%+2.1f%%" % (ret*100)
		sys.stdout.write(x)

	sys.stdout.write("\n\nFund Daily Sharpe Ratio (for year):")
	for year in years:
		year_vals=[]
		for date in funds.index:
			if(date.year==year):
				year_vals.append(funds[date])
		ret=tsu.getRatio(year_vals)
		x="\t%+2.1f" % ret
		sys.stdout.write(x)

	sys.stdout.write("\n$SPX Daily Sharpe Ratio(for year):")         
	for year in years:
		year_vals=[]
		for date in SPX_CLOSE.index:
			if(date.year==year):
				year_vals.append(SPX_CLOSE.xs(date))
		ret=tsu.getRatio(year_vals)
		x="\t%+2.1f" % ret
		sys.stdout.write(x)
	
	sys.stdout.write("\n\nMonthly Returns %\n\t")
	month_names=du.getMonthNames()
	for name in month_names:
		sys.stdout.write("\t"+str(name))
	sys.stdout.write("\n")
	years=du.getYears(funds)
	i=0
	mrets=tsu.monthly(funds)
	for year in years:
		sys.stdout.write(str(year)+"\t")
		months=du.getMonths(funds,year)
		for month in months:
			x="\t%+2.1f" % (mrets[i]*100)
			sys.stdout.write(x)
			i+=1
		sys.stdout.write("\n")


def print_old_stats(funds, name, html_file):
	#montly returns
	mrets=tsu.monthly(funds)
	html_file.write("<H1>"+str(name)+"</H1>\n")
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
	ratio=0
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
	

def generate_report(funds_list, graph_names, out_file):
	html_file = open("report.html","w")
	print_header(html_file, out_file)
	html_file.write("<IMG SRC=\'./funds.png\' width=400/>\n")
	html_file.write("<BR/>\n\n")
	i=0
	plt.clf()
	#load spx for time frame
	symbol=["$SPX"]
	start_date=0
	end_date=0
	for fund in funds_list:
		if(type(fund)!=type(list())):
			if(start_date==0 or start_date>fund.index[0]):
				start_date=fund.index[0]	
			if(end_date==0 or end_date<fund.index[-1]):
				end_date=fund.index[-1]	
			mult=10000/fund.values[0]
			plt.plot(fund.index, fund.values*mult,label=path.basename(graph_names[i]))
		else:	
			if(start_date==0 or start_date>fund[0].index[0]):
				start_date=fund[0].index[0]	
			if(end_date==0 or end_date<fund[0].index[-1]):
				end_date=fund[0].index[-1]	
			mult=10000/fund[0].values[0]
			plt.plot(fund[0].index, fund[0].values*mult, label=path.basename(graph_names[i]))	
		i+=1
	timeofday=dt.timedelta(hours=16)
	timestamps=du.getNYSEdays(start_date, end_date, timeofday)
	dataobj=da.DataAccess('Norgate')
	global SPX_CLOSE
	SPX_CLOSE=dataobj.get_data(timestamps,symbol, "close", verbose=False)
	mult=10000/SPX_CLOSE.values[0]
	i=0
	for fund in funds_list:
		if(type(fund)!=type(list())):
			print_stats(fund, ["$SPX"], graph_names[i])
		else:	
			print_stats(fund[0], ["$SPX"], graph_names[i])
		i+=1
	plt.plot(SPX_CLOSE.index,SPX_CLOSE.values*mult,label="SSPX")
	plt.ylabel('Fund Value')
	plt.xlabel('Date')
	plt.legend()
	plt.draw()
	savefig('funds.png', format='png')
	print_footer(html_file)

def generate_robust_report(file, out_file):
	html_file = open(filename,"w")
	print_header(html_file, out_file)
	converter.fundsToPNG(funds,'funds.png')
	html_file.write("<H2>QSTK Generated Report:"+filename+"</H2>\n")
	html_file.write("<IMG SRC=\'./funds.png\'/>\n")
	html_file.write("<IMG SRC=\'./analysis.png\'/>\n")
	html_file.write("<BR/>\n\n")
	fund=cPickle.load(file)
	#add funds to graph
	#add analysis
	print_stats(fund, html_file)
	print_footer(html_file)

if __name__ == '__main__':
	# Usage
	#
	# Normal:
	# python report.py 'out.pkl' ['out2.pkl' ...]
	#
	# Robust:
	# python report.py -r 'out.pkl'
	#
	
	robust=0

	if(sys.argv[1]=='-r'):
		robust=1

	filename = "report.html"
	
	if(robust==1):
		input=open(sys.argv[2],"r")
		funds=cPickle.load(input)
		generate_robust_report(funds,filename)
	else:
		files=sys.argv
		files.remove(files[0])
		funds=[]
		for file in files:
			input=open(file,"r")
			fund=cPickle.load(input)
			funds.append(fund)
		generate_report(funds, files, filename)


