'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on April, 20, 2012

@author: Sourabh Bajaj
@contact: sourabh@sourabhbajaj.com
@summary: Visualizer - Data Access files 

'''

#import libraries
import numpy as np
import time
import qstkutil.tsutil as tsu
import datetime as dt
import pickle
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from pylab import *
from pandas import *
import os
from PyQt4 import QtGui, QtCore, Qt


# Changes made in the featutil file are : Edited the getFeatureFuncs()


def ReadData(DataFile, TimeTag, IDTag, FactorTag):
	#Reading the timestamps from a text file.
	timestamps=[]
	file = open(TimeTag, 'r')
	for onedate in file.readlines():
		timestamps.append(dt.datetime.strptime(onedate, "%Y-%m-%d\n"))
	file.close()

	symbols=[]
	file = open(IDTag, 'r')
	for f in file.readlines():
		j = f[:-1]
		symbols.append(j)
	file.close()

	# Reading the Data Values
	Numpyarray=pickle.load(open( DataFile, 'rb' ))
	
	for i in range(0,len(Numpyarray)):
		tsu.fillforward(Numpyarray[i])
		tsu.fillbackward(Numpyarray[i])

	featureslist=[]
	file = open(FactorTag, 'r')
	for f in file.readlines():
		j = f[:-1]
		featureslist.append(j)
	file.close()

	PandasObject= Panel(Numpyarray, items=featureslist, major_axis=timestamps, minor_axis=symbols)
	featureslist.sort()
	return (PandasObject, featureslist, symbols, timestamps)

def DataParameter(PandasObject, featureslist, symbols, timestamps):
	
	startday=timestamps[0]
	endday=timestamps[-1]
	MinFeat=[]
	MaxFeat=[]

	for feature in featureslist:
		MinFeat.append(np.amin(np.min(PandasObject[feature], axis=0)))
		MaxFeat.append(np.amax(np.max(PandasObject[feature], axis=0)))

	dMinFeat=dict(zip(featureslist, MinFeat))
	dMaxFeat=dict(zip(featureslist, MaxFeat))
	
	return(dMinFeat, dMaxFeat, startday, endday)


def GetData(directorylocation):

	DataFile = directorylocation + 'ALLDATA.pkl'
	TimeTag=directorylocation + 'TimeStamps.txt'
	IDTag=directorylocation + 'Symbols.txt'
	FactorTag=directorylocation + 'Features.txt'	

	(PandasObject, featureslist, symbols, timestamps)=ReadData(DataFile, TimeTag, IDTag, FactorTag)
	(dMinFeat, dMaxFeat, startday, endday)=DataParameter(PandasObject, featureslist, symbols, timestamps)
	return (PandasObject, featureslist, symbols, timestamps,dMinFeat, dMaxFeat, startday, endday)


if __name__ == '__main__':
	directorylocation = os.environ['QS']+'/Tools/Visualizer/Data/Dow_2009-01-01_2010-12-31/'
	GetData(directorylocation)
	print "The access functions are working"
