#created by Sourabh Bajaj
#email: sourabhbajaj90@gmail.com

#import libraries
import numpy as np
import time
import qstkutil.dateutil as du
import qstkutil.tsutil as tsu
import qstkutil.DataAccess as da
import qstkfeat.featutil as feat
import datetime as dt
import pickle
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from pylab import *
from pandas import *


# Changes made in the featutil file are : Edited the getFeatureFuncs()


def ReadData(DataFile='ALLDATA.pkl', TimeTag='TimeStamps.txt', IDTag='Symbols.txt', FactorTag='Features.txt'):
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


def main():
	(PandasObject, featureslist, symbols, timestamps)=ReadData()
	(dMinFeat, dMaxFeat, startday, endday)=DataParameter(PandasObject, featureslist, symbols, timestamps)
	print "The access functions are working"

if __name__ == '__main__':
	main()

