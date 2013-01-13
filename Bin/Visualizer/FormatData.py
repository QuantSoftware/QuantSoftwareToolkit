'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on April, 20, 2012

@author: Sourabh Bajaj
@contact: sourabhbajaj90@gmail.com
@summary: Visualizer - Random Data Source - Weather Data

'''

#import libraries
import numpy as np
import datetime as dt
import pickle
import dircache
import os
import string
import datetime as dt
from pylab import *
from pandas import *
import qstkutil.tsutil as tsu

def genData():
	
	op_folderpath = os.environ['QS'] + 'Tools/Visualizer/Data/Norway'
	ip_folderpath = os.environ['QS'] + 'Tools/Visualizer/Data/Norway/Raw/'
	
	if not os.path.exists(op_folderpath):
		os.mkdir(op_folderpath)
		print "Data was missing"
		return
	op_folderpath = op_folderpath + '/'	

	files_at_this_path = dircache.listdir(ip_folderpath)
	ip_folderpath = ip_folderpath +'/'
	
	stationnames = []
	startyears = []
	endyears=[]

	for file1 in files_at_this_path:
		file = open(ip_folderpath + file1, 'r')
		for f in file.readlines():
			if string.find(f, 'Name')!=-1:
				n= string.lstrip(f, 'Name= ')
				stationnames.append(string.rstrip(n))
			if string.find(f, 'Start year')!=-1:
				n= string.lstrip(f, 'Start year= ')
				startyears.append(int(string.rstrip(n)))
			if string.find(f, 'End year')!=-1:
				n= string.lstrip(f, 'End year= ')
				endyears.append(int(string.rstrip(n)))
		file.close()

	timestamps = [ dt.datetime(year,1,1) for year in range(min(startyears),max(endyears)+1)]

	months = ['January','February','March','April','May','June','July','August','September','October','November','December']

	numpyarray = np.empty([len(months),len(timestamps),len(stationnames)])
	numpyarray[:] = np.NAN

	PandasObject= Panel(numpyarray, items=months, major_axis=timestamps, minor_axis=stationnames)

	for i, file1 in enumerate(files_at_this_path):
		flag=0
		station=stationnames[i]
		file = open(ip_folderpath + file1, 'r')
		for f in file.readlines():
			if flag==1:
				data=string.split(f)
				year = int(data.pop(0))
				time = dt.datetime(year,1,1)
				for month,val in zip(months,data):
					PandasObject[month][station][time] = float(val)
			if string.find(f, 'Obs')!=-1:
				flag=1
		file.close()

	#Creating a txt file of timestamps
	file = open(op_folderpath +'TimeStamps.txt', 'w')
	for onedate in timestamps:
		stringdate=dt.date.isoformat(onedate)
		file.write(stringdate+'\n')
	file.close()

	#Creating a txt file of symbols
	file = open(op_folderpath +'Symbols.txt', 'w')
	for sym in stationnames:
		file.write(str(sym)+'\n')
	file.close()

	#Creating a txt file of Features
	file = open(op_folderpath +'Features.txt', 'w')
	for f in months:
		file.write(f+'\n')
	file.close()
	
	Numpyarray_Final = PandasObject.values
	for i,month in enumerate(months):
		for j,station in enumerate(stationnames):
			for k in range(len(timestamps)-1):
				if np.isnan(Numpyarray_Final[i][k+1][j]):
					Numpyarray_Final[i][k+1][j] = Numpyarray_Final[i][k][j]

	for i,month in enumerate(months):
		for j,station in enumerate(stationnames):
			for z in range(1,len(timestamps)):
				k = len(timestamps) - z
				if np.isnan(Numpyarray_Final[i][k-1][j]):
					Numpyarray_Final[i][k-1][j] = Numpyarray_Final[i][k][j]

	pickle.dump(Numpyarray_Final,open(op_folderpath +'ALLDATA.pkl', 'wb' ),-1)


def main():
	genData()

if __name__ == '__main__':
	main()
