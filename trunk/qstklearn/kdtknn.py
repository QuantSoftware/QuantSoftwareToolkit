"""
A simple wrapper for scipy.spatial.kdtree.KDTree for doing KNN
"""
import math,random,sys,bisect,time
import numpy,scipy.spatial.distance, scipy.spatial.kdtree
import cProfile,pstats,gendata
import numpy as np

class kdtknn(object):
	"""
	A simple wrapper of scipy.spatial.kdtree.KDTree
	
	Since the scipy KDTree implementation does not allow for incrementally adding
	data points, the entire KD-tree is rebuilt on the first call to 'query' after a
	call to 'addEvidence'. For this reason it is more efficient to add training data
	in batches.
	"""
	def __init__(self,k=3,method='mean'):
		"""
		Basic setup.
		"""
		self.data = None
		self.kdt = None
		self.rebuild_tree = True
		self.k = k
		self.method = method

	def addEvidence(self,dataX,dataY=None):
		"""
		@summary: Add training data
		@param dataX: Data to add, either entire set with classification as last column, or not if
		              the Y data is provided explicitly.  Must be same width as previously appended data.
		@param dataY: Optional, can be used 
		
		'data' should be a numpy array matching the same dimensions as any data 
		provided in previous calls to addEvidence, with dataY as the 
		training label.
		"""
		
		''' Slap on Y column if it is provided, if not assume it is there '''
		if not dataY == None:
			data = numpy.zeros([dataX.shape[0],dataX.shape[1]+1])
			data[:,0:dataX.shape[1]]=dataX
			data[:,(dataX.shape[1])]=dataY
		else:
			data = dataX
		
		self.rebuild_tree = True
		if self.data is None:
			self.data = data
		else:
			self.data = numpy.append(self.data,data,axis=0)

	def rebuildKDT(self):
		"""
		Force the internal KDTree to be rebuilt.
		"""
		self.kdt = scipy.spatial.kdtree.KDTree(self.data[:,:-1])
		self.rebuild_tree = False
	
	def query(self,points,k=None,method=None):
		"""
		Classify a set of test points given their k nearest neighbors.
		
		'points' should be a numpy array with each row corresponding to a specific query.
		Returns the estimated class according to supplied method (currently only 'mode'
		and 'mean' are supported)
		"""
		if k is None:
			k = self.k
		if method is None:
			method = self.method
		if self.rebuild_tree is True:
			if self.data is None:
				return None
			self.rebuildKDT()
		#kdt.query returns a list of distances and a list of indexes into the
		#data array
		tmp = self.kdt.query(points,k)
		if k == 1:
			#in the case of k==1, numpy fudges an array of 1 dimension into
			#a scalar, so we handle it seperately. tmp[1] is the list of
			#indecies, tmp[1][0] is the first one (we only need one),
			#self.data[tmp[1][0]] is the data point corresponding to the
			#first neighbor, and self.data[tmp[1][0]][-1] is the last column
			#which is the class of the neighbor.
			return self.data[tmp[1][0]][-1]
		#for all the neighbors returned by kdt.query, get their class and stick that into a list
		n_clsses = map(lambda rslt: map(lambda p: p[-1], self.data[rslt]), self.kdt.query(points,k)[1])
		if method=='mode':
			return map(lambda x: scipy.stats.stats.mode(x)[0],n_clsses)[0]
		elif method=='mean':
			return numpy.array(map(lambda x: numpy.mean(x),n_clsses))
		elif method=='median':
			return numpy.array(map(lambda x: numpy.median(x),n_clsses))
		elif method=='raw':
			return numpy.array(n_clsses)

def getflatcsv(fname):
	inf = open(fname)
	return numpy.array([map(float,s.strip().split(',')) for s in inf.readlines()])

def testgendata():
	fname = 'test2.dat'
	querys = 1000
	d = 2
	k=3
	bnds = ((-10,10),)*d
	clsses = (0,1)
	data = getflatcsv(fname)
	kdt = kdtknn(k,method='mode')
	kdt.addEvidence(data)
	kdt.rebuildKDT()
	stime = time.time()
	for x in xrange(querys):
		pnt = numpy.array(gendata.gensingle(d,bnds,clsses))
		reslt = kdt.query(numpy.array([pnt[:-1]]))
		print pnt,"->",reslt
	etime = time.time()
	print etime-stime,'/',querys,'=',(etime-stime)/float(querys),'avg wallclock time per query'
	#foo.addEvidence(data[:,:-1],data[:,-1])
	#foo.num_checks = 0
	#for x in xrange(querys):
	#	pnt = numpy.array(gendata.gensingle(d,bnds,clsses))
	#	foo.query(pnt[:-1],3)
	#	if x % 50 == 0:
	#		print float(foo.num_checks)/float(x+1),
	#		print x,"/",querys
	#print "Average # queries:", float(foo.num_checks)/float(querys)
	
def test():
	testgendata()

if __name__=="__main__":
	test()
	#prof= cProfile.Profile()
	#prof.run('test()')
	#stats = pstats.Stats(prof)
	#stats.sort_stats("cumulative").print_stats()
