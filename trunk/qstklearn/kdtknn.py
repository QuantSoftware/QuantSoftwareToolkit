"""
A simple wrapper for scipy.spatial.kdtree.KDTree for doing KNN
"""
import math,random,sys,bisect,time
import numpy,scipy.spatial.distance, scipy.spatial.kdtree
import knn,cProfile,pstats,gendata

class KDTKNN:
	"""
	A simple wrapper of scipy.spatial.kdtree.KDTree
	
	Since the scipy KDTree implementation does not allow for incrementally adding
	data points, the entire KD-tree is rebuilt on the first call to 'query' after a
	call to 'addEvidence'. For this reason it is more efficient to add training data
	in batches.
	"""
	def __init__(self):
		"""
		Basic setup.
		"""
		self.data = None
		self.kdt = None
		self.rebuild_tree = True
	def addEvidence(self,data):
		"""
		Add training data. 
		
		'data' should be a numpy array matching the same dimensions as any data 
		provided in previous calls to addEvidence, with the last column as the 
		training label.
		"""
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
	
	def query(self,points,k,method='mode'):
		"""
		Classify a set of test points given their k nearest neighbors.
		
		'points' should be a numpy array with each row corresponding to a specific query.
		Returns the estimated class according to supplied method (currently only 'mode'
		and 'mean' are supported)
		"""
		if self.rebuild_tree is True:
			if self.data is None:
				return None
			self.rebuildKDT()
		n_clsses = map(lambda rslt: map(lambda p: p[-1], self.data[rslt]), self.kdt.query(points,k)[1])
		if method=='mode':
			return numpy.array(map(lambda x: scipy.stats.stats.mode(x)[0],n_clsses))
		elif method=='mean':
			return numpy.array(map(lambda x: numpy.mean(x),n_clsses))

def getflatcsv(fname):
	inf = open(fname)
	return numpy.array([map(float,s.strip().split(',')) for s in inf.readlines()])

def testgendata():
	fname = 'test2.dat'
	querys = 1000
	d = 2
	bnds = ((-10,10),)*d
	clsses = (0,1)
	data = getflatcsv(fname)
	kdt = KDTKNN()
	kdt.addEvidence(data)
	kdt.rebuildKDT()
	stime = time.time()
	for x in xrange(querys):
		pnt = numpy.array(gendata.gensingle(d,bnds,clsses))
		reslt = kdt.query(numpy.array([pnt[:-1]]),k=3)
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
