"""
This package is an implementation of a novel improvement to KNN which
speeds up query times
"""
import math,random,sys,bisect,time
import numpy,scipy.spatial.distance

def adistfun(u,v):
	#assuming 1xN ndarrays
	#return math.sqrt(((u-v)**2).sum())
	#return ((u-v)**2).sum()
	tmp = (u-v)
	return math.sqrt(numpy.dot(tmp,tmp))

class FastKNN:
	"""
	A class which implements the KNN learning algorithm with sped up
	query times.

	This class follows the conventions of other classes in the qstklearn
	module, with a constructor that initializes basic parameters and
	bookkeeping variables, an 'addEvidence' method for adding labeled
	training data individually or as a batch, and a 'query' method
	that returns an estimated class for an unlabled point.  Training
	and testing data are in the form of numpy arrays, and classes are
	discrete.
	
	In order to speed up query times, this class keeps a number of lists which
	sort the training data by distance to 'anchor' points.  The lists aren't
	sorted until the first call to the 'query' method, after which, the lists
	are kept in sorted order. Initial sort is done using pythons 'sort'
	(samplesort), and sorted insertions with 'insort' from the bisect module.
	"""
	def __init__(self, num_anchors):
		"""
		Creates a new FastKNN object that will use the given number of 
		anchors.
		"""
		self.num_anchors = num_anchors
		self.training_data = list()
		self.anchors = list()
		self.data_by_anchors = dict()
		self.data_classes = dict()
		self.is_sorted = False
		#self.distfun = scipy.spatial.distance.euclidean
		self.distfun = adistfun
		self.num_checks = 0
	
	def resetAnchors(self,selection_type='random'):
		"""
		Picks a new set of anchors.  The anchor lists will be re-sorted upon
		the next call to 'query'.
		
		selection_type - the method to use when selecting new anchor points.
		'random' performs a random permutation of the training points and
		picks the first 'num_anchors' as new anchors.
		"""
		if selection_type == 'random':
			self.anchors = range(len(self.training_data))
			random.shuffle(self.anchors)
			self.anchors = self.anchors[0:self.num_anchors]
		self.is_sorted = False
				
	
	def addEvidence(self,data,label):
		"""
		Adds to the set of training data. If the anchor lists were sorted
		before the call to this method, the new data will be inserted into
		the anchor lists using 'bisect.insort'
		
		data - a numpy array, either a single point (1D) or a set of
		points (2D)
		
		label - the label for data. A single value, or a list of values
		in the same order as the points in data.
		"""
		if len(data.shape)==1:
			new_idx = len(self.training_data)
			self.traning_data.append(data)
			self.data_classes[new_idx] = label
			if self.is_sorted:
				for a in self.anchors:
					dist = self.distfun(data,self.training_data[a])
					bisect.insort(self.data_by_anchors[a],(dist,new_idx))
		elif len(data.shape)>1:
			for i in xrange(len(data)):
				thing = data[i]
				new_idx = len(self.training_data)
				self.training_data.append(thing)
				self.data_classes[new_idx] = label[i]
				if self.is_sorted:
					for a in self.anchors:
						dist = self.distfun(thing,self.training_data[a])
						bisect.insort(self.data_by_anchors[a],(dist,new_idx))
	
	def query(self,point,k,method='mode'):
		"""
		Returns class value for an unlabled point by examining its k nearest
		neighbors. 'method' determines how the class of the unlabled point is
		determined.
		"""
		#stime = time.time()
		if len(self.anchors) < self.num_anchors:
			self.resetAnchors()
		if not self.is_sorted:
			for a in self.anchors:
				self.data_by_anchors[a] = [ ( self.distfun(self.training_data[datai],self.training_data[a]), datai) for datai in range(len(self.training_data))]
				self.data_by_anchors[a].sort(key=lambda pnt: pnt[0])
		#select the anchor to search from
		#right now pick the anchor closest to the query point
		anchor = self.anchors[0]
		anchor_dist = self.distfun(point,self.training_data[anchor]) 
		for i in xrange(1,len(self.anchors)):
			new_anchor = self.anchors[i]
			new_anchor_dist = self.distfun(point,self.training_data[new_anchor])
			if new_anchor_dist < anchor_dist:
				anchor = new_anchor
				anchor_dist = new_anchor_dist
		#now search through the list
		anchor_list = self.data_by_anchors[anchor]
		neighbors = list()
		for i in xrange(0,len(anchor_list)):
			nextpnt_dist = self.distfun(point,self.training_data[anchor_list[i][1]])
			#self.num_checks += 1
			nextthing = (nextpnt_dist,anchor_list[i][1])
			bisect.insort(neighbors,nextthing)
			if len(neighbors) > k:
				neighbors = neighbors[0:k]
				if anchor_dist + neighbors[k-1][0] < anchor_list[i][0]:
					break
		#we have the k neighbors, report the class
		#of the query point via method
		if method == 'mode':
			class_count = dict()
			for n in neighbors:
				nid = n[1]
				clss = self.data_classes[nid]
				if clss in class_count:
					tmp = class_count[clss]
				else:
					tmp = 0
				class_count[clss] = tmp+1
			rv = max(class_count.iteritems(),key=lambda item:item[1])[0]
		#etime = time.time()
		#print "Query time:", etime-stime
		return rv

#def test():
#	for leftout in xrange(1,11):
#		print "Fold",leftout
#		foo = FastKNN(10)
#		for x in xrange(1,11):
#			if x != leftout:
#				somedata = open("spiral/spiralfold%d.txt" % x)
#				pnts = list()
#				clss = list()
#				for line in somedata:
#					pbbbt,x,y = line.split()
#					x,y = float(x),float(y)
#					pnts.append((x,y))
#					clss.append(line.split()[0])
#				somedata.close()
#				pnts = numpy.array(pnts)
#				foo.addEvidence(pnts,clss)
#		somedata = open("spiral/spiralfold%d.txt" % leftout)
#		correct = total = 0
#		for line in somedata:
#			pbbbt,x,y = line.split()
#			x,y = float(x),float(y)
#			guess=foo.query((x,y),10)
#			#print guess, pbbbt
#			if guess == pbbbt:
#				correct += 1
#			total += 1
#		print correct,"/",total,":",float(correct)/float(total)
#		#print "Average number of checks per query:", 
#		print float(foo.num_checks)/float(total)
