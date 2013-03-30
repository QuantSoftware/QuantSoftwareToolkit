########################################
# A brief introduction to numpy arrays #
########################################
#
# Prereqs: Basic python. "import", built-in data types (numbers, lists, 
#          strings), range
#
# This short tutorial is mostly about introducing numpy arrays, how they're
# different from basic python lists/tuples, and the various ways you can
# manipulate them.  It's intended to be both a runnable python script, and
# a step by step tutorial. 
#
# This tutorial does NOT cover
# 	1) Installing numpy/dependencies. For that see 
#
#			http://docs.scipy.org/doc/numpy/user/install.html
#
#	2) Basic python. This includes getting, installing, running the python
#		interpreter, the basic python data types (strings, numbers, sequences),
#		if statements, or for loops. If you're new to python an excellent place
#		to start is here:
#
#			http://docs.python.org/2/tutorial/
#
#	3) Any numpy libraries in depth. It may include references to utility
#		functions where necessary, but this is strictly a tutorial for 
#		beginners. More advanced documentation is available here:
#
#			(Users guide)
#			http://docs.scipy.org/doc/numpy/user/index.html
#			(Reference documentation)
#			http://docs.scipy.org/doc/numpy/reference/
#
#
#
#
## Lets get started!
print "Importing numpy"
import numpy as np

## This loads the numpy library and lets us refer to it by the shorthand "np",
## which is the convention used in the numpy documentation and in many
## online tutorials/examples 

print "Creating arrays"
## Now lets make an array to play around with. You can make numpy arrays in
## a number of ways,
## Filled with zeros:
zeroArray = np.zeros( (2,3) ) # [[ 0.  0.  0.]
print zeroArray               #  [ 0.  0.  0.]]

## Or ones:
oneArray = np.ones( (2,3) )   # [[ 1.  1.  1.]
print oneArray                #  [ 1.  1.  1.]]

## Or filled with junk:
emptyArray = np.empty( (2,3) ) 
print emptyArray

## Note, emptyArray might look random, but it's just uninitialized which means
## you shouldn't count on it having any particular data in it, even random
## data! If you do want random data you can use random():
randomArray = np.random.random( (2,3) )
print randomArray

## If you're following along and trying these commands out, you should have
## noticed that making randomArray took a lot longer than emptyArray. That's
## because np.random.random(...) is actually using a random number generator
## to fill in each of the spots in the array with a randomly sampled number
## from 0 to 1.

## You can also create an array by hand:
foo = [ [1,2,3],
        [4,5,6]]

myArray = np.array(foo) # [[1 2 3] 
print myArray           #  [4 5 6]]


print "Reshaping arrays"
## Of course, if you're typing out a range for a larger matrix, it's easier to
## use arange(...):
rangeArray = np.arange(6,12).reshape( (2,3) ) # [[ 6  7  8]
print rangeArray                              #  [ 9 10 11]]

## there's two things going on here. First, the arange(...) function returns a
## 1D array similar to what you'd get from using the built-in python function
## range(...) with the same arguments, except it returns a numpy array
## instead of a list.
print np.arange(6,12) # [ 6  7  8  9 10 11 12]

## the reshape method takes the data in an existing array, and stuffs it into
## an array with the given shape and returns it.  
print rangeArray.reshape( (3,2) ) # [[ 6  7]
                                  #  [ 8  9]
                                  #  [10 11]]

#The original array doesn't change though.
print rangeArray # [[ 6  7  8]
                 #  [ 9 10 11]

## When you use reshape(...) the total number of things in the array must stay
## the same. So reshaping an array with 2 rows and 3 columns into one with 
## 3 rows and 2 columns is fine, but 3x3 or 1x5 won't work
#print rangeArray.reshape( (3,3) ) #ERROR
squareArray = np.arange(1,10).reshape( (3,3) ) #this is fine, 9 elements


print "Accessing array elements"
## Accessing an array is also pretty straight forward. You access a specific
## spot in the table by referring to its row and column inside square braces
## after the array:
print rangeArray[0,1] #7

## Note that row and column numbers start from 0, not 1! Numpy also lets you 
## refer to ranges inside an array:
print rangeArray[0,0:2] #[6 7]
print squareArray[0:2,0:2] #[[1 2]  # the top left corner of squareArray
                           # [4 5]]

## These ranges work just like slices and python lists. n:m:t specifies a range
## that starts at n, and stops before m, in steps of size t. If any of these 
## are left off, they're assumed to be the start, the end+1, and 1 respectively
print squareArray[:,0:3:2] #[[1 3]   #skip the middle column
                           # [4 6]
                           # [7 9]]

## Also like python lists, you can assign values to specific positions, or
## ranges of values to slices
squareArray[0,:] = np.array(range(1,4)) #set the first row to 1,2,3
squareArray[1,1] = 0                    # set the middle spot to zero
squareArray[2,:] = 1                    # set the last row to ones
print squareArray                       # [[1 2 3]
                                        #  [4 0 6]
                                        #  [1 1 1]]

## Something new to numpy arrays is indexing using an array of indices:
fibIndices = np.array( [1, 1, 2, 3] )
randomRow = np.random.random( (10,1) ) # an array of 10 random numbers
print randomRow
print randomRow[fibIndices] # the first, first, second and third element of
                             # randomRow 

## You can also use an array of true/false values to index:
boolIndices = np.array( [[ True, False,  True],
                          [False,  True, False],
                          [ True, False,  True]] )
print squareArray[boolIndices] # a 1D array with the selected values
                                # [1 3 0 1 1]

## It gets a little more complicated with 2D (and higher) arrays.  You need
## two index arrays for a 2D array:
rows = np.array( [[0,0],[2,2]] ) #get the corners of our square array
cols = np.array( [[0,2],[0,2]] )
print squareArray[rows,cols]     #[[1 3]
                                 # [1 1]]
boolRows = np.array( [False, True, False] ) # just the middle row
boolCols = np.array( [True, False, True] )  # Not the middle column
print squareArray[boolRows,boolCols]        # [4 6]

print "Operations on arrays"
## One useful trick is to create a boolean matrix based on some test and use
## that as an index in order to get the elements of a matrix that pass the
## test:
sqAverage = np.average(squareArray) # average(...) returns the average of all
                                    # the elements in the given array
betterThanAverage = squareArray > sqAverage
print betterThanAverage             #[[False False  True]
                                    # [ True False  True]
                                    # [False False False]]
print squareArray[betterThanAverage] #[3 4 6]

## Indexing like this can also be used to assign values to elements of the
## array. This is particularly useful if you want to filter an array, say by 
## making sure that all of its values are above/below a certain threshold:
sqStdDev = np.std(squareArray) # std(...) returns the standard deviation of
                               # all the elements in the given array
clampedSqArray = np.array(squareArray.copy(), dtype=float) 
                                    # make a copy of squareArray that will
                                    # be "clamped". It will only contain
                                    # values within one standard deviation
                                    # of the mean. Values that are too low
                                    # or to high will be set to the min
                                    # and max respectively. We set 
                                    # dtype=float because sqAverage
                                    # and sqStdDev are floating point
                                    # numbers, and we don't want to 
                                    # truncate them down to integers.
clampedSqArray[ (squareArray-sqAverage) > sqStdDev ] = sqAverage+sqStdDev
clampedSqArray[ (squareArray-sqAverage) < -sqStdDev ] = sqAverage-sqStdDev
print clampedSqArray # [[ 1.          2.          3.        ]
                     #  [ 3.90272394  0.31949828  3.90272394]
                     #  [ 1.          1.          1.        ]]


## Multiplying and dividing arrays by numbers does what you'd expect. It
## multiples/divides element-wise
print squareArray * 2 # [[ 2  4  6]
                      #  [ 8  0 12]
                      #  [ 2  2  2]]

## Addition works similarly:
print squareArray + np.ones( (3,3) ) #[[2 3 4]
                                     # [5 1 7]
                                     # [2 2 2]]

## Multiplying two arrays together (of the same size) is also element wise
print squareArray * np.arange(1,10).reshape( (3,3) ) #[[ 1  4  9]
                                                     # [16  0 36]
                                                     # [ 7  8  9]]

## Unless you use the dot(...) function, which does matrix multiplication
## from linear algebra:
matA = np.array( [[1,2],[3,4]] )
matB = np.array( [[5,6],[7,8]] )
print np.dot(matA,matB) #[[19 22]
                        # [43 50]]

## And thats it! There's a lot more to the numpy library, and there are a few
## things I skipped over here, such as what happens when array dimensions
## don't line up when you're indexing or multiplying them together, so if 
## you're interested, I strongly suggest you head over to the scipy wiki's
## numpy tutorial for a more in depth look at using numpy arrays:
##
##			http://www.scipy.org/Tentative_NumPy_Tutorial
