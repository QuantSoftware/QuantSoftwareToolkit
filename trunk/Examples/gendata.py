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

part1 = numpy.random.normal(loc=[0.5,0.5],scale=[.25,.25],size=[333,2])
part2 = numpy.random.normal(loc=[-.5,-.5],scale=.25,size=[150,2])
part2 = numpy.concatenate((part2,numpy.random.normal(loc=[0.6,1.2],scale=.1,size=[183,2])),axis=0)
part3 = numpy.random.normal(loc=[-.5,.5],scale=.5,size=[334,2])

#
# squish in X
#
#part1[:,1] = part1[:,1]/4
#part2[:,1] = part2[:,1]/4
#part3[:,1] = part3[:,1]/4

f = open('data1.csv', 'w')
for i in range(0,part1.shape[0]-1):
	#prnstr = str(part1[i,0])+','+str(part1[i,1])+','+str(part1y[i])+'\n'
	prnstr = str(part1[i,0])+','+str(part1[i,1])+',1.0'+'\n'
	f.write(prnstr)
for i in range(0,part2.shape[0]-1):
	prnstr = str(part2[i,0])+','+str(part2[i,1])+',-1.0'+'\n'
	f.write(prnstr)
for i in range(0,part3.shape[0]-1):
	prnstr = str(part3[i,0])+','+str(part3[i,1])+',0.0'+'\n'
	f.write(prnstr)
f.close()
