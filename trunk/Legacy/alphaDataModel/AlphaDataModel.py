'''
Created on Jun 1, 2010

@author: Shreyas Joshi
@summary: The purpose of this module is to make it easy to create hdf5 files with "alpha" values in them
'''
import tables as pt
fileName="defaultAlphaFileName.h5"
h5f=[]
group=[]
table=[]
opened=False    
ctr=float (0.0)    

class AlphaDataModelClass(pt.IsDescription):  
    symbol = pt.StringCol(30)
    exchange = pt.StringCol(10) 
    alphaValue=pt.Float32Col() 
    timestamp= pt.Time64Col() 
    
    
    
    def __init__(self):
        print "In the AlphaDataModelClass constructor"
        
    #constructor done
#class ends!

    
def openFile (newFileName):
        '''
        @param newFileName: Full path to the file and the name of the file.
        @summary: This function creates a new file. If the length of the name passed =0 then a file called "defaultAlphaFileName.h5" will be created.
        @warning: If a file of the same name already exists then that file will be overwritten.
        '''
        global fileName, h5f, group, table, opened, ctr
        ctr=float (0.0)
        
        if newFileName is None:
            print "Using default name for alpha file"
        else:
           if (len(newFileName)>0):
               fileName= str(newFileName)
           else:
             print "Using default name for alpha file"
            
        #Opening the file now...
        if not opened:
         h5f = pt.openFile(str(fileName), mode = "w")
         group = h5f.createGroup("/", 'alphaData')
         table = h5f.createTable(group, 'alphaData', AlphaDataModelClass)   
         opened=True 
        else:
         print "File already opened. Doing nothing"      
    
    # File opened    
    
def addRow (currSymbol, currExchange, currAlphaVal, currTS):
    '''
    @param currSymbol: The symbol of the stock
    @param currExchange: The exchange the stock trades on
    @param currAlphaVal: The alpha value of the stock at the current timestamp
    @param currTS: The current time stamp
    @summary: Adds a row of data to the file- and writes it out do disk...eventually
    @warning: File must be opened before calling this function   
    '''
    global ctr
    
    if opened:
        ctr= ctr + 1
        row = table.row
        row['symbol']= currSymbol
        row['exchange']=currExchange
        row['alphaValue']= currAlphaVal
        row['timestamp']= currTS
        row.append()
        #print "Appending row " + str (currTS)
        if (ctr==10000): #Might cause mem error
          ctr=0
          table.flush() #write to disk
    
    
    
    else:
       print "ERROR: File not open. Can not add row."  
       raise IOError   
#    addRow done


#def readAllData():
##  global h5f
##  table2 = h5f.root.alphaData.alphaData
#  
#  for row in table.iterrows():  #for row in table2.iterrows():
#      print "SYM: "+str(row['symbol'])+", EX: "+ str(row['exchange'])+", ALPHA: "+str(row['alphaValue'])+", TIMESTAMP: "+str(row['timestamp'])
    
    
def closeFile():
        '''
        @summary: closes the file.
        '''
        
        table.flush()
        h5f.close()
        print str(fileName)+ " closed."
        opened= False