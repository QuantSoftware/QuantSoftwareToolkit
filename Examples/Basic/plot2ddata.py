#
# How to plot 2D data for learning
#
# by Tucker Balch
# September 2010
#

#
# imports
#
import numpy as np
import matplotlib.pyplot as plt
from pylab import *
import datetime as dt

#
# read in and slice up the data
#
data = np.loadtxt('data2.csv',delimiter=',',skiprows=1)
X1 = data[:,0]
X2 = data[:,1]
Y  = data[:,2]

#
# Choose colors
#
miny = min(Y)
maxy = max(Y)
Y = (Y-miny)/(maxy-miny)
colors =[]
for i in Y:
	if (i>0.5):
		j = (i-.5)*2
		colors.append([j,(1-j),0])
	else:
		j = i*2
		colors.append([0,j,(1-j)])

#
# scatter plot X1 vs X2 and colors are Y
#
plt.clf()
plt.scatter(X1,X2,c=colors,edgecolors='none')
plt.xlabel('X1')
plt.ylabel('X2')
plt.xlim(-2,2)	# set x scale
plt.ylim(-2,2)	# set y scale
savefig("scatterdata.pdf", format='pdf')
