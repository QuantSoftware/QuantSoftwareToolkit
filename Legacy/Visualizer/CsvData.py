'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on April, 20, 2012

@author: Sourabh Bajaj
@contact: sourabh@sourabhbajaj.com
@summary: Visualizer - Data reading from a CSV

'''

#import libraries
import numpy as np
import datetime as dt
import pickle
import os
import matplotlib.pyplot as plt
from pylab import *
from pandas import *
import csv

def csv_Dataconverter(datadirectory, ip_path):
	op_folderpath = os.environ['QS'] + 'Tools/Visualizer/Data/' + datadirectory
	if not os.path.exists(op_folderpath):
		os.mkdir(op_folderpath)
	op_folderpath = op_folderpath + '/'

	f = open(ip_path)
	data = csv.reader(f)
	fields = data.next()

	featureslist = fields[2:]
	timestamps=[]
	seen_timestamps = set()
	symbols=[]
	seen_symbols =set()

	for row in data:
		timestamp = dt.datetime.strptime(row[0], "%Y-%m-%d")
		tag = row[1]
		if timestamp not in seen_timestamps:
			timestamps.append(timestamp)
			seen_timestamps.add(timestamp)
		if tag not in seen_symbols:
			seen_symbols.add(tag)
			symbols.append(tag)

	numpyarray = np.empty([len(featureslist),len(timestamps),len(symbols)])
	numpyarray[:] = np.NAN

	PandasObject= Panel(numpyarray, items=featureslist, major_axis=timestamps, minor_axis=symbols)

	f.close()	

	data = csv.reader(open(ip_path))
	data.next()

	for row in data:
		timestamp = dt.datetime.strptime(row[0], "%Y-%m-%d")
		tag = row[1] 
		row1 = row[2:]
		for feat, val  in zip(featureslist, row1):
			try:
				PandasObject[feat][tag][timestamp] = float(val)
			except: 
				continue

	#Creating a txt file of timestamps
	file = open(op_folderpath +'TimeStamps.txt', 'w')
	for onedate in timestamps:
		stringdate=dt.date.isoformat(onedate)
		file.write(stringdate+'\n')
	file.close()

	#Creating a txt file of symbols
	file = open(op_folderpath +'Symbols.txt', 'w')
	for sym in symbols:
		file.write(str(sym)+'\n')
	file.close()

	#Creating a txt file of Features
	file = open(op_folderpath +'Features.txt', 'w')
	for f in featureslist:
		file.write(f+'\n')
	file.close()
	
	Numpyarray_Final = PandasObject.values
	for i,feat in enumerate(featureslist):
		for j,tag in enumerate(symbols):
			for k in range(len(timestamps)-1):
				if np.isnan(Numpyarray_Final[i][k+1][j]):
					Numpyarray_Final[i][k+1][j] = Numpyarray_Final[i][k][j]

	for i,feat in enumerate(featureslist):
		for j,tag in enumerate(symbols):
			for z in range(1,len(timestamps)):
				k = len(timestamps) - z
				if np.isnan(Numpyarray_Final[i][k-1][j]):
					Numpyarray_Final[i][k-1][j] = Numpyarray_Final[i][k][j]

	pickle.dump(Numpyarray_Final,open(op_folderpath +'ALLDATA.pkl', 'wb' ),-1)

	print 'All data has been converted'

def main():
	datadirectory = 'TestCSV'
	ip_path = os.environ['QS'] + '/Tools/Visualizer/Data/Raw/Test.csv'
	csv_Dataconverter(datadirectory, ip_path)

if __name__ == '__main__':
	main()
