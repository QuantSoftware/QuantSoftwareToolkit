'''
Created on Apr 22, 2011

@author: shreyas
@summary: This is intended to be a collection of helper routines used by different QSTK modules
'''

import dircache
import os

def clean_paths (paths_to_clean):
 '''
 @summary: Removes any previous files in the list of paths.
 '''

 if (type(paths_to_clean) is str):
    temp= paths_to_clean
    paths_to_clean= list()
    paths_to_clean.append(temp)
    #endif
    
 
 for path in paths_to_clean:
    files_at_this_path = dircache.listdir(str(path))
    for _file in files_at_this_path:
        if (os.path.isfile(path + _file)):
            os.remove(path + _file)
            #if ends 
    #for ends
 #outer for ends   
    
#clean_output_paths  ends