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


def ReadData(DataFile='AllData', TimeTag='TimeStamps.txt', IDTag='Symbols.csv', FactorTag='TMPFeatures.csv'):

	#Reading the timestamps from a text file.
	timestamps=[]
	file = open(TimeTag, 'r')
	for onedate in file.readlines():
		timestamps.append(dt.datetime.strptime(onedate, "%Y-%m-%d\n"))
	file.close()

	# Reading the ID Tag
	symbols=np.loadtxt(IDTag,dtype='S5',comments='#',skiprows=1,)

	# Reading the Data Values
	Numpyarray=pickle.load(open( DataFile, 'rb' ))
	
	for i in range(0,len(Numpyarray)):
		tsu.fillforward(Numpyarray[i])
		tsu.fillbackward(Numpyarray[i])

	# Reading the Factor Tags
	featureslist= np.loadtxt(FactorTag,dtype='S',comments='#',skiprows=1,)

	PandasObject= Panel(Numpyarray, items=featureslist, major_axis=timestamps, minor_axis=symbols)

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

def PlotParam(PandasObject, dayofplot, XFeat,XMin, XMax, YFeat,YMin, YMax, ZFeat,ZMin, ZMax, SizeFeat, ColorFeat):

	xs=PandasObject[XFeat].xs(dayofplot)
	ys=PandasObject[YFeat].xs(dayofplot)
	zs=PandasObject[ZFeat].xs(dayofplot)
	
	size=PandasObject[SizeFeat].xs(dayofplot)
	color=PandasObject[SizeFeat].xs(dayofplot)
	
	fig = figure()
	ax = fig.gca(projection='3d')
	
	ax.scatter(xs,ys,zs,marker='o', alpha=0.5, c=color, s=size)

	ax.set_xlim(XMin, XMax)
	ax.set_ylim(YMin, YMax)
	ax.set_zlim(ZMin, ZMax)	
	
	ax.set_xlabel(XFeat)
	ax.set_ylabel(YFeat)
	ax.set_zlabel(ZFeat)

	plt.show()

def main():
	(PandasObject, featureslist, symbols, timestamps)=ReadData()
	(dMinFeat, dMaxFeat, startday, endday)=DataParameter(PandasObject, featureslist, symbols, timestamps)
	
	PlotParam(PandasObject, timestamps[16], featureslist[10], dMinFeat[featureslist[10]], dMaxFeat[featureslist[10]], featureslist[8], dMinFeat[featureslist[8]], dMaxFeat[featureslist[8]],featureslist[9], dMinFeat[featureslist[9]], dMaxFeat[featureslist[9]], featureslist[0], featureslist[5])
	
if __name__ == '__main__':
	main()

