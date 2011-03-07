#
# gendata.py
#
# Generate example data for machine learning tests.
#
# Tucker Balch
# Nov 10, 2010
#
import numpy
import math

#
# Makes a ripple effect
#
#part1 = numpy.random.normal(loc=[0,0],scale=[5,5],size=[10000,2])
#part1y = part1[:,0]*part1[:,0] + part1[:,1]*part1[:,1]
#part1y = numpy.sqrt(part1[:,0]**2 + part1[:,1]**2)
#part1y = numpy.sin(part1y)

part1 = numpy.random.normal(loc=[.5,.5,.5],scale=.25,size=[334,3])
part2 = numpy.random.normal(loc=[-.5,-.5,.5],scale=.25,size=[151,3])
part2 = numpy.concatenate((part2,numpy.random.normal(loc=[.6,1.2,.5],
	scale=.1,size=[184,3])),axis=0)
part3 = numpy.random.normal(loc=[-.5,.5,.5],scale=.5,size=[334,3])

part1[:,2] = 1
part2[:,2] = 0
part3[:,2] = -1

alldata = numpy.concatenate([part1,part2,part3])
p = numpy.random.permutation(alldata.shape[0])
alldata = alldata[p,:]

#
# squish in X
#
alldata[:,1] = alldata[:,1]/4

f = open('data2.csv', 'w')
for i in range(0,alldata.shape[0]-1):
	prnstr = str(alldata[i,0])+','+str(alldata[i,1])+',' \
		+str(alldata[i,2])+'\n'
	f.write(prnstr)
f.close()
