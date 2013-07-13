'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on Jan 15, 2013

@author: Sourabh Bajaj
@contact: sourabhbajaj@gatech.edu
@summary: Data Access python library.

'''

import numpy as np
import pandas as pa
import os
import re
import csv
import pickle as pkl
import time
import datetime as dt
import dircache
import tempfile
import copy

class Exchange (object):
    AMEX = 1
    NYSE = 2
    NYSE_ARCA = 3
    OTC = 4
    DELISTED = 5
    NASDAQ = 6


class DataItem (object):
    OPEN = "open"
    HIGH = "high"
    LOW = "low"
    CLOSE = "close"
    VOL = "volume"
    VOLUME = "volume"
    ACTUAL_CLOSE = "actual_close"
    ADJUSTED_CLOSE = "adj_close"
    # Compustat label list pulled from _analyze() in compustat_csv_to_pkl.py
    COMPUSTAT = ['gvkey', 'fyearq', 'fqtr', 'fyr', 'ACCTSTDQ', 'ADRRQ', 'AJEXQ', 'AJPQ', 'CURRTRQ', 'CURUSCNQ', 'PDQ', 'PDSA', 'PDYTD', 'SCFQ', 'SRCQ', 'UPDQ', 'ACCDQ', 'ACCHGQ', 'ACCOQ', 'ACOMINCQ', 'ACOQ', 'ACOXQ', 'ACTQ', 'ADPACQ', 'ALTOQ', 'AMQ', 'ANCQ', 'ANOQ', 'AOCIDERGLQ', 'AOCIOTHERQ', 'AOCIPENQ', 'AOCISECGLQ', 'AOL2Q', 'AOQ', 'AOTQ', 'APOQ', 'APQ', 'AQAQ', 'AQDQ', 'AQEPSQ', 'AQPL1Q', 'AQPQ', 'ARCED12', 'ARCEDQ', 'ARCEEPS12', 'ARCEEPSQ', 'ARCEQ', 'ARTFSQ', 'ATQ', 'AUL3Q', 'AUTXRQ', 'BCEFQ', 'BCTQ', 'BDIQ', 'CAPCSTQ', 'CAPR1Q', 'CAPR2Q', 'CAPR3Q', 'CAPRTQ', 'CAPSQ', 'CAQ', 'CEQQ', 'CFBDQ', 'CFEREQ', 'CFOQ', 'CFPDOQ', 'CHEQ', 'CHQ', 'CHSQ', 'CIBEGNIQ', 'CICURRQ', 'CIDERGLQ', 'CIMIIQ', 'CIOTHERQ', 'CIPENQ', 'CIQ', 'CISECGLQ', 'CITOTALQ', 'CLTQ', 'COGSQ', 'CSH12Q', 'CSHFDQ', 'CSHIQ', 'CSHOPQ', 'CSHOQ', 'CSHPRQ', 'CSTKEQ', 'CSTKQ', 'DCOMQ', 'DFPACQ', 'DFXAQ', 'DILADQ', 'DILAVQ', 'DITQ', 'DLCQ', 'DLTTQ', 'DOQ', 'DPACREQ', 'DPACTQ', 'DPQ', 'DPRETQ', 'DPTBQ', 'DPTCQ', 'DRCQ', 'DRLTQ', 'DTEAQ', 'DTEDQ', 'DTEEPSQ', 'DTEPQ', 'DVPDPQ', 'DVPQ', 'DVRREQ', 'DVTQ', 'EPSF12', 'EPSFIQ', 'EPSFXQ', 'EPSPIQ', 'EPSPXQ', 'EPSX12', 'EQRTQ', 'EROQ', 'ESOPCTQ', 'ESOPNRQ', 'ESOPRQ', 'ESOPTQ', 'ESUBQ', 'FCAQ', 'FEAQ', 'FELQ', 'FFOQ', 'GDWLAMQ', 'GDWLIA12', 'GDWLIAQ', 'GDWLID12', 'GDWLIDQ', 'GDWLIEPS12', 'GDWLIEPSQ', 'GDWLIPQ', 'GDWLQ', 'GLAQ', 'GLCEA12', 'GLCEAQ', 'GLCED12', 'GLCEDQ', 'GLCEEPS12', 'GLCEEPSQ', 'GLCEPQ', 'GLDQ', 'GLEPSQ', 'GLPQ', 'GPQ', 'HEDGEGLQ', 'IATIQ', 'IBADJ12', 'IBADJQ', 'IBCOMQ', 'IBKIQ', 'IBMIIQ', 'IBQ', 'ICAPTQ', 'IDITQ', 'IIREQ', 'IITQ', 'INTACCQ', 'INTANOQ', 'INTANQ', 'INTCQ', 'INVFGQ', 'INVOQ', 'INVRMQ', 'INVTQ', 'INVWIPQ', 'IOBDQ', 'IOIQ', 'IOREQ', 'IPQ', 'IPTIQ', 'ISGTQ', 'ISTQ', 'IVAEQQ', 'IVAOQ', 'IVIQ', 'IVLTQ', 'IVPTQ', 'IVSTQ', 'IVTFSQ', 'LCABGQ', 'LCACUQ', 'LCOQ', 'LCOXQ', 'LCTQ', 'LLTQ', 'LNOQ', 'LOL2Q', 'LOQ', 'LOXDRQ', 'LQPL1Q', 'LSEQ', 'LSQ', 'LTMIBQ', 'LTQ', 'LUL3Q', 'MIBNQ', 'MIBQ', 'MIBTQ', 'MIIQ', 'MSAQ', 'MTLQ', 'NCOQ', 'NIITQ', 'NIMQ', 'NIQ', 'NITQ', 'NOPIOQ', 'NOPIQ', 'NPATQ', 'NRTXTDQ', 'NRTXTEPSQ', 'NRTXTQ', 'OEPF12', 'OEPS12', 'OEPSXQ', 'OIADPQ', 'OIBDPQ', 'OPEPSQ', 'OPROQ', 'OPTDRQ', 'OPTFVGRQ', 'OPTLIFEQ', 'OPTRFRQ', 'OPTVOLQ', 'PCLQ', 'PIQ', 'PLLQ', 'PNC12', 'PNCD12', 'PNCDQ', 'PNCEPS12', 'PNCEPSQ', 'PNCIAPQ', 'PNCIAQ', 'PNCIDPQ', 'PNCIDQ', 'PNCIEPSPQ', 'PNCIEPSQ', 'PNCIPPQ', 'PNCIPQ', 'PNCPD12', 'PNCPDQ', 'PNCPEPS12', 'PNCPEPSQ', 'PNCPQ', 'PNCQ', 'PNCWIAPQ', 'PNCWIAQ', 'PNCWIDPQ', 'PNCWIDQ', 'PNCWIEPQ', 'PNCWIEPSQ', 'PNCWIPPQ', 'PNCWIPQ', 'PNRSHOQ', 'PPEGTQ', 'PPENTQ', 'PRCAQ', 'PRCD12', 'PRCDQ', 'PRCE12', 'PRCEPS12', 'PRCEPSQ', 'PRCPD12', 'PRCPDQ', 'PRCPEPS12', 'PRCPEPSQ', 'PRCPQ', 'PRCQ', 'PRCRAQ', 'PRSHOQ', 'PSTKNQ', 'PSTKQ', 'PSTKRQ', 'PTRANQ', 'PVOQ', 'PVTQ', 'RATIQ', 'RAWMSMQ', 'RCAQ', 'RCDQ', 'RCEPSQ', 'RCPQ', 'RDIPAQ', 'RDIPDQ', 'RDIPEPSQ', 'RDIPQ', 'RECCOQ', 'RECDQ', 'RECTAQ', 'RECTOQ', 'RECTQ', 'RECTRQ', 'RECUBQ', 'REITQ', 'REQ', 'RETQ', 'REUNAQ', 'REVTQ', 'RISQ', 'RLLQ', 'RLTQ', 'RRA12', 'RRAQ', 'RRD12', 'RRDQ', 'RREPS12', 'RREPSQ', 'RRPQ', 'RVLRVQ', 'RVTIQ', 'RVUTXQ', 'SAAQ', 'SALEQ', 'SALQ', 'SBDCQ', 'SCOQ', 'SCQ', 'SCTQ', 'SEQOQ', 'SEQQ', 'SETA12', 'SETAQ', 'SETD12', 'SETDQ', 'SETEPS12', 'SETEPSQ', 'SETPQ', 'SPCE12', 'SPCED12', 'SPCEDPQ', 'SPCEDQ', 'SPCEEPS12', 'SPCEEPSP12', 'SPCEEPSPQ', 'SPCEEPSQ', 'SPCEP12', 'SPCEPD12', 'SPCEPQ', 'SPCEQ', 'SPIDQ', 'SPIEPSQ', 'SPIOAQ', 'SPIOPQ', 'SPIQ', 'SRETQ', 'SSNPQ', 'STKCHQ', 'STKCOQ', 'STKCPAQ', 'TDSGQ', 'TDSTQ', 'TEQQ', 'TFVAQ', 'TFVCEQ', 'TFVLQ', 'TIEQ', 'TIIQ', 'TRANSAQ', 'TSTKNQ', 'TSTKQ', 'TXDBAQ', 'TXDBQ', 'TXDIQ', 'TXDITCQ', 'TXPQ', 'TXTQ', 'TXWQ', 'UACOQ', 'UAOQ', 'UAPTQ', 'UCAPSQ', 'UCCONSQ', 'UCEQQ', 'UDDQ', 'UDMBQ', 'UDOLTQ', 'UDPCOQ', 'UDVPQ', 'UGIQ', 'UINVQ', 'ULCOQ', 'UNIAMIQ', 'UNNPQ', 'UNOPINCQ', 'UOPIQ', 'UPDVPQ', 'UPMCSTKQ', 'UPMPFQ', 'UPMPFSQ', 'UPMSUBPQ', 'UPSTKCQ', 'UPSTKQ', 'URECTQ', 'USPIQ', 'USUBDVPQ', 'USUBPCVQ', 'UTEMQ', 'WCAPQ', 'WDAQ', 'WDDQ', 'WDEPSQ', 'WDPQ', 'XAGTQ', 'XBDTQ', 'XCOMIQ', 'XCOMQ', 'XDVREQ', 'XIDOQ', 'XINTQ', 'XIOQ', 'XIQ', 'XIVIQ', 'XIVREQ', 'XOBDQ', 'XOIQ', 'XOPROQ', 'XOPRQ', 'XOPT12', 'XOPTD12', 'XOPTD12P', 'XOPTDQ', 'XOPTDQP', 'XOPTEPS12', 'XOPTEPSP12', 'XOPTEPSQ', 'XOPTEPSQP', 'XOPTQ', 'XOPTQP', 'XOREQ', 'XPPQ', 'XRDQ', 'XRETQ', 'XSGAQ', 'XSQ', 'XSTOQ', 'XSTQ', 'XTQ', 'ACCHGY', 'ACCLIY', 'ACQDISNY', 'ACQDISOY', 'ADPACY', 'AFUDCCY', 'AFUDCIY', 'AMCY', 'AMY', 'AOLOCHY', 'APALCHY', 'APCHY', 'AQAY', 'AQCY', 'AQDY', 'AQEPSY', 'AQPY', 'ARCEDY', 'ARCEEPSY', 'ARCEY', 'ASDISY', 'ASINVY', 'ATOCHY', 'AUTXRY', 'BCEFY', 'BCTY', 'BDIY', 'CAPCSTY', 'CAPFLY', 'CAPXFIY', 'CAPXY', 'CDVCY', 'CFBDY', 'CFEREY', 'CFLAOTHY', 'CFOY', 'CFPDOY', 'CHECHY', 'CHENFDY', 'CIBEGNIY', 'CICURRY', 'CIDERGLY', 'CIMIIY', 'CIOTHERY', 'CIPENY', 'CISECGLY', 'CITOTALY', 'CIY', 'COGSY', 'CSHFDY', 'CSHPRY', 'CSTKEY', 'DCSFDY', 'DCUFDY', 'DEPCY', 'DFXAY', 'DILADY', 'DILAVY', 'DISPOCHY', 'DITY', 'DLCCHY', 'DLTISY', 'DLTRY', 'DOCY', 'DOY', 'DPCY', 'DPRETY', 'DPY', 'DTEAY', 'DTEDY', 'DTEEPSY', 'DTEPY', 'DVPDPY', 'DVPY', 'DVRECY', 'DVRREY', 'DVTY', 'DVY', 'EIEACY', 'EPSFIY', 'EPSFXY', 'EPSPIY', 'EPSPXY', 'EQDIVPY', 'ESUBCY', 'ESUBY', 'EXRESY', 'EXREUY', 'EXREY', 'FCAY', 'FFOY', 'FIAOY', 'FINCFY', 'FININCY', 'FINLEY', 'FINREY', 'FINVAOY', 'FOPOXY', 'FOPOY', 'FOPTY', 'FSRCOPOY', 'FSRCOPTY', 'FSRCOY', 'FSRCTY', 'FUSEOY', 'FUSETY', 'GDWLAMY', 'GDWLIAY', 'GDWLIDY', 'GDWLIEPSY', 'GDWLIPY', 'GLAY', 'GLCEAY', 'GLCEDY', 'GLCEEPSY', 'GLCEPY', 'GLDY', 'GLEPSY', 'GLPY', 'GPY', 'HEDGEGLY', 'IBADJY', 'IBCOMY', 'IBCY', 'IBKIY', 'IBMIIY', 'IBY', 'IDITY', 'IIREY', 'IITY', 'INTANDY', 'INTANPY', 'INTCY', 'INTFACTY', 'INTFLY', 'INTIACTY', 'INTOACTY', 'INTPDY', 'INTPNY', 'INTRCY', 'INVCHY', 'INVDSPY', 'INVSVCY', 'IOBDY', 'IOIY', 'IOREY', 'IPTIY', 'ISGTY', 'ITCCY', 'IVACOY', 'IVCHY', 'IVIY', 'IVNCFY', 'IVSTCHY', 'LIQRESNY', 'LIQRESOY', 'LNDEPY', 'LNINCY', 'LNMDY', 'LNREPY', 'LTDCHY', 'LTDLCHY', 'LTLOY', 'MICY', 'MIIY', 'MISEQY', 'NCFLIQY', 'NCOY', 'NEQMIY', 'NIITY', 'NIMY', 'NITY', 'NIY', 'NOASUBY', 'NOPIOY', 'NOPIY', 'NRTXTDY', 'NRTXTEPSY', 'NRTXTY', 'OANCFCY', 'OANCFDY', 'OANCFY', 'OEPSXY', 'OIADPY', 'OIBDPY', 'OPEPSY', 'OPPRFTY', 'OPROY', 'OPTDRY', 'OPTFVGRY', 'OPTLIFEY', 'OPTRFRY', 'OPTVOLY', 'PCLY', 'PDVCY', 'PIY', 'PLIACHY', 'PLLY', 'PNCDY', 'PNCEPSY', 'PNCIAPY', 'PNCIAY', 'PNCIDPY', 'PNCIDY', 'PNCIEPSPY', 'PNCIEPSY', 'PNCIPPY', 'PNCIPY', 'PNCPDY', 'PNCPEPSY', 'PNCPY', 'PNCWIAPY', 'PNCWIAY', 'PNCWIDPY', 'PNCWIDY', 'PNCWIEPSY', 'PNCWIEPY', 'PNCWIPPY', 'PNCWIPY', 'PNCY', 'PRCAY', 'PRCDY', 'PRCEPSY', 'PRCPDY', 'PRCPEPSY', 'PRCPY', 'PROSAIY', 'PRSTKCCY', 'PRSTKCY', 'PRSTKPCY', 'PRVY', 'PSFIXY', 'PTRANY', 'PURTSHRY', 'PVOY', 'RAWMSMY', 'RCAY', 'RCDY', 'RCEPSY', 'RCPY', 'RDIPAY', 'RDIPDY', 'RDIPEPSY', 'RDIPY', 'RECCHY', 'REITY', 'REVTY', 'RISY', 'RRAY', 'RRDY', 'RREPSY', 'RRPY', 'RVY', 'SALEY', 'SCSTKCY', 'SETAY', 'SETDY', 'SETEPSY', 'SETPY', 'SHRCAPY', 'SIVY', 'SPCEDPY', 'SPCEDY', 'SPCEEPSPY', 'SPCEEPSY', 'SPCEPY', 'SPCEY', 'SPIDY', 'SPIEPSY', 'SPIOAY', 'SPIOPY', 'SPIY', 'SPPCHY', 'SPPEY', 'SPPIVY', 'SPSTKCY', 'SRETY', 'SSTKY', 'STFIXAY', 'STINVY', 'STKCHY', 'STKCOY', 'STKCPAY', 'SUBDISY', 'SUBPURY', 'TDCY', 'TDSGY', 'TFVCEY', 'TIEY', 'TIIY', 'TSAFCY', 'TXACHY', 'TXBCOFY', 'TXBCOY', 'TXDCY', 'TXDIY', 'TXOPY', 'TXPDY', 'TXTY', 'TXWY', 'TXY', 'UAOLOCHY', 'UDFCCY', 'UDVPY', 'UFRETSDY', 'UGIY', 'UNIAMIY', 'UNOPINCY', 'UNWCCY', 'UOISY', 'UPDVPY', 'UPTACY', 'USPIY', 'USTDNCY', 'USUBDVPY', 'UTFDOCY', 'UTFOSCY', 'UTMEY', 'UWKCAPCY', 'WCAPCHCY', 'WCAPCHY', 'WCAPCY', 'WCAPOPCY', 'WCAPSAY', 'WCAPSUY', 'WCAPSY', 'WCAPTY', 'WCAPUY', 'WDAY', 'WDDY', 'WDEPSY', 'WDPY', 'XAGTY', 'XBDTY', 'XCOMIY', 'XCOMY', 'XDVREY', 'XIDOCY', 'XIDOY', 'XINTY', 'XIOY', 'XIVIY', 'XIVREY', 'XIY', 'XOBDY', 'XOIY', 'XOPROY', 'XOPRY', 'XOPTDQPY', 'XOPTDY', 'XOPTEPSQPY', 'XOPTEPSY', 'XOPTQPY', 'XOPTY', 'XOREY', 'XRDY', 'XRETY', 'XSGAY', 'XSTOY', 'XSTY', 'XSY', 'XTY', 'DLRSN', 'FYRC', 'GGROUP', 'GIND', 'GSECTOR', 'GSUBIND', 'NAICS', 'PRIUSA', 'SIC', 'SPCINDCD', 'SPCSECCD', 'STKO']


class DataSource(object):
    NORGATE = "Norgate"
    YAHOO = "Yahoo"
    YAHOOold = "YahooOld"
    COMPUSTAT = "Compustat"
    CUSTOM = "Custom"
    MLT = "ML4Trading"
    #class DataSource ends


class DataAccess(object):
    '''
    @summary: This class is used to access all the symbol data. It readin in pickled numpy arrays converts them into appropriate pandas objects
    and returns that object. The {main} function currently demonstrates use.
    @note: The earliest time for which this works is platform dependent because the python date functionality is platform dependent.
    '''
    def __init__(self, sourcein=DataSource.YAHOO, s_datapath=None,
                 s_scratchpath=None, cachestalltime=12, verbose=False):
        '''
        @param sourcestr: Specifies the source of the data. Initializes paths based on source.
        @note: No data is actually read in the constructor. Only paths for the source are initialized
        @param: Scratch defaults to a directory in /tmp/QSScratch
        '''

        self.folderList = list()
        self.folderSubList = list()
        self.cachestalltime = cachestalltime
        self.fileExtensionToRemove = ".pkl"

        try:
            self.rootdir = os.environ['QSDATA']
            try:
                self.scratchdir = os.environ['QSSCRATCH']
            except:
                self.scratchdir = os.path.join(tempfile.gettempdir(), 'QSScratch')
        except:
            if s_datapath != None:
                self.rootdir = s_datapath
                if s_scratchpath != None:
                    self.scratchdir = s_scratchpath
                else:
                    self.scratchdir = os.path.join(tempfile.gettempdir(), 'QSScratch')
            else:
                self.rootdir = os.path.join(os.path.dirname(__file__), '..', 'QSData')
                self.scratchdir = os.path.join(tempfile.gettempdir(), 'QSScratch')

        if verbose:
            print "Scratch Directory: ", self.scratchdir
            print "Data Directory: ", self.rootdir

        if not os.path.isdir(self.rootdir):
            print "Data path provided is invalid"
            raise

        if not os.path.exists(self.scratchdir):
            os.mkdir(self.scratchdir)

        if (sourcein == DataSource.NORGATE):

            self.source = DataSource.NORGATE
            self.midPath = "/Processed/Norgate/Stocks/"

            self.folderSubList.append("/US/AMEX/")
            self.folderSubList.append("/US/NASDAQ/")
            self.folderSubList.append("/US/NYSE/")
            self.folderSubList.append("/US/NYSE Arca/")
            self.folderSubList.append("/US/OTC/")
            self.folderSubList.append("/US/Delisted Securities/")
            self.folderSubList.append("/US/Indices/")

            for i in self.folderSubList:
                self.folderList.append(self.rootdir + self.midPath + i)

        elif (sourcein == DataSource.CUSTOM):
            self.source = DataSource.CUSTOM
            self.folderList.append(self.rootdir + "/Processed/Custom/")

        elif (sourcein == DataSource.MLT):
            self.source = DataSource.MLT
            self.folderList.append(self.rootdir + "/ML4Trading/")

        elif (sourcein == DataSource.YAHOO):
            self.source = DataSource.YAHOO
            self.folderList.append(self.rootdir + "/Yahoo/")
            self.fileExtensionToRemove = ".csv"

        elif (sourcein == DataSource.COMPUSTAT):
            self.source = DataSource.COMPUSTAT
            self.midPath = "/Processed/Compustat"
            #What if these paths don't exist?
            self.folderSubList.append("/US/NASDAQ/")
            self.folderSubList.append("/US/NYSE/")
            self.folderSubList.append("/US/AMEX/")

            for i in self.folderSubList:
                self.folderList.append(self.rootdir + self.midPath + i)
            #if DataSource.Compustat ends

        else:
            raise ValueError("Incorrect data source requested.")

        #__init__ ends

    def get_data_hardread(self, ts_list, symbol_list, data_item, verbose=False, bIncDelist=False):
        '''
        Read data into a DataFrame no matter what.
        @param ts_list: List of timestamps for which the data values are needed. Timestamps must be sorted.
        @param symbol_list: The list of symbols for which the data values are needed
        @param data_item: The data_item needed. Like open, close, volume etc.  May be a list, in which case a list of DataFrame is returned.
        @param bIncDelist: If true, delisted securities will be included.
        @note: If a symbol is not found then a message is printed. All the values in the column for that stock will be NaN. Execution then
        continues as usual. No errors are raised at the moment.
        '''

        ''' Now support lists of items, still support old string behaviour '''
        bStr = False
        if( isinstance( data_item, str) ):
            data_item = [data_item]
            bStr = True

        # init data struct - list of arrays, each member is an array corresponding do a different data type
        # arrays contain n rows for the timestamps and m columns for each stock
        all_stocks_data = []
        for i in range( len(data_item) ):
            all_stocks_data.append( np.zeros ((len(ts_list), len(symbol_list))) );
            all_stocks_data[i][:][:] = np.NAN
        
        list_index= []
        
        ''' For each item in the list, add to list_index (later used to delete non-used items) '''
        for sItem in data_item:
            if( self.source == DataSource.CUSTOM ) :
                ''' If custom just load what you can '''
                if (sItem == DataItem.CLOSE):
                    list_index.append(1)
                elif (sItem == DataItem.ACTUAL_CLOSE):
                    list_index.append(2)
            if( self.source == DataSource.COMPUSTAT ):
                ''' If compustat, look through list of features '''
                for i, sLabel in enumerate(DataItem.COMPUSTAT):
                    if sItem == sLabel:
                        ''' First item is date index, labels start at 1 index '''
                        list_index.append(i+1)
                        break
                else:
                    raise ValueError ("Incorrect value for data_item %s"%sItem)
            
            if( self.source == DataSource.NORGATE ):
                if (sItem == DataItem.OPEN):
                    list_index.append(1)
                elif (sItem == DataItem.HIGH):
                    list_index.append (2)
                elif (sItem ==DataItem.LOW):
                    list_index.append(3)
                elif (sItem == DataItem.CLOSE):
                    list_index.append(4)
                elif(sItem == DataItem.VOL):
                    list_index.append(5)
                elif (sItem == DataItem.ACTUAL_CLOSE):
                    list_index.append(6)
                else:
                    #incorrect value
                    raise ValueError ("Incorrect value for data_item %s"%sItem)

            if( self.source == DataSource.MLT or self.source == DataSource.YAHOO):
                if (sItem == DataItem.OPEN):
                    list_index.append(1)
                elif (sItem == DataItem.HIGH):
                    list_index.append (2)
                elif (sItem ==DataItem.LOW):
                    list_index.append(3)
                elif (sItem == DataItem.ACTUAL_CLOSE):
                    list_index.append(4)
                elif(sItem == DataItem.VOL):
                    list_index.append(5)
                elif (sItem == DataItem.CLOSE):
                    list_index.append(6)
                else:
                    #incorrect value
                    raise ValueError ("Incorrect value for data_item %s"%sItem)
                #end elif
        #end data_item loop

        #read in data for a stock
        symbol_ctr=-1
        for symbol in symbol_list:
            _file = None
            symbol_ctr = symbol_ctr + 1
            #print self.getPathOfFile(symbol)
            try:
                if (self.source == DataSource.CUSTOM) or (self.source == DataSource.MLT)or (self.source == DataSource.YAHOO):
                    file_path= self.getPathOfCSVFile(symbol);
                else:
                    file_path= self.getPathOfFile(symbol);
                
                ''' Get list of other files if we also want to include delisted '''
                if bIncDelist:
                    lsDelPaths = self.getPathOfFile( symbol, True )
                    if file_path == None and len(lsDelPaths) > 0:
                        print 'Found delisted paths:', lsDelPaths
                
                ''' If we don't have a file path continue... unless we have delisted paths '''
                if (type (file_path) != type ("random string")):
                    if bIncDelist == False or len(lsDelPaths) == 0:
                        continue; #File not found
                
                if not file_path == None: 
                    _file = open(file_path, "rb")
            except IOError:
                # If unable to read then continue. The value for this stock will be nan
                print _file
                continue;
                
            assert( not _file == None or bIncDelist == True )
            ''' Open the file only if we have a valid name, otherwise we need delisted data '''
            if _file != None:
                if (self.source==DataSource.CUSTOM) or (self.source==DataSource.YAHOO)or (self.source==DataSource.MLT):
                    creader = csv.reader(_file)
                    row=creader.next()
                    row=creader.next()
                    #row.pop(0)
                    for i, item in enumerate(row):
                        if i==0:
                            try:
                                date = dt.datetime.strptime(item, '%Y-%m-%d')
                                date = date.strftime('%Y%m%d')
                                row[i] = float(date)
                            except:
                                date = dt.datetime.strptime(item, '%m/%d/%y')
                                date = date.strftime('%Y%m%d')
                                row[i] = float(date)
                        else:
                            row[i]=float(item)
                    naData=np.array(row)
                    for row in creader:
                        for i, item in enumerate(row):
                            if i==0:
                                try:
                                    date = dt.datetime.strptime(item, '%Y-%m-%d')
                                    date = date.strftime('%Y%m%d')
                                    row[i] = float(date)
                                except:
                                    date = dt.datetime.strptime(item, '%m/%d/%y')
                                    date = date.strftime('%Y%m%d')
                                    row[i] = float(date)
                            else: 
                                row[i]=float(item)
                        naData=np.vstack([np.array(row),naData])
                else:
                    naData = pkl.load (_file)
                _file.close()
            else:
                naData = None
                
            ''' If we have delisted data, prepend to the current data '''
            if bIncDelist == True and len(lsDelPaths) > 0 and naData == None:
                for sFile in lsDelPaths[-1:]:
                    ''' Changed to only use NEWEST data since sometimes there is overlap (JAVA) '''
                    inFile = open( sFile, "rb" )
                    naPrepend = pkl.load( inFile )
                    inFile.close()
                    
                    if naData == None:
                        naData = naPrepend
                    else:
                        naData = np.vstack( (naPrepend, naData) )
                        
            #now remove all the columns except the timestamps and one data column
            if verbose:
                print self.getPathOfFile(symbol)
            
            ''' Fix 1 row case by reshaping '''
            if( naData.ndim == 1 ):
                naData = naData.reshape(1,-1)
                
            #print naData
            #print list_index
            ''' We open the file once, for each data item we need, fill out the array in all_stocks_data '''
            for lLabelNum, lLabelIndex in enumerate(list_index):
                
                ts_ctr = 0
                b_skip = True
                
                ''' select timestamps and the data column we want '''
                temp_np = naData[:,(0,lLabelIndex)]
                
                #print temp_np
                
                num_rows= temp_np.shape[0]

                
                symbol_ts_list = range(num_rows) # preallocate
                for i in range (0, num_rows):

                    timebase = temp_np[i][0]
                    timeyear = int(timebase/10000)
                    
                    # Quick hack to skip most of the data
                    # Note if we skip ALL the data, we still need to calculate
                    # last time, so we know nothing is valid later in the code
                    if timeyear < ts_list[0].year and i != num_rows - 1:
                        continue
                    elif b_skip == True:
                        ts_ctr = i
                        b_skip = False
                    
                    
                    timemonth = int((timebase-timeyear*10000)/100)
                    timeday = int((timebase-timeyear*10000-timemonth*100))
                    timehour = 16
    
                    #The earliest time it can generate a time for is platform dependent
                    symbol_ts_list[i]=dt.datetime(timeyear,timemonth,timeday,timehour) # To make the time 1600 hrs on the day previous to this midnight
                    
                #for ends
    
    
                #now we have only timestamps and one data column
                
                
                #Skip data from file which is before the first timestamp in ts_list
    
                while (ts_ctr < temp_np.shape[0]) and (symbol_ts_list[ts_ctr] < ts_list[0]):
                    ts_ctr=  ts_ctr+1
                    
                    #print "skipping initial data"
                    #while ends
                
                for time_stamp in ts_list:
                    
                    if (symbol_ts_list[-1] < time_stamp):
                        #The timestamp is after the last timestamp for which we have data. So we give up. Note that we don't have to fill in NaNs because that is 
                        #the default value.
                        break;
                    else:
                        while ((ts_ctr < temp_np.shape[0]) and (symbol_ts_list[ts_ctr]< time_stamp)):
                            ts_ctr = ts_ctr+1
                            #while ends
                        #else ends
                                            
                    #print "at time_stamp: " + str(time_stamp) + " and symbol_ts "  + str(symbol_ts_list[ts_ctr])
                    
                    if (time_stamp == symbol_ts_list[ts_ctr]):
                        #Data is present for this timestamp. So add to numpy array.
                        #print "    adding to numpy array"
                        if (temp_np.ndim > 1): #This if is needed because if a stock has data for 1 day only then the numpy array is 1-D rather than 2-D
                            all_stocks_data[lLabelNum][ts_list.index(time_stamp)][symbol_ctr] = temp_np [ts_ctr][1]
                        else:
                            all_stocks_data[lLabelNum][ts_list.index(time_stamp)][symbol_ctr] = temp_np [1]
                        #if ends
                        
                        ts_ctr = ts_ctr +1
                    
                #inner for ends
            #outer for ends
        #print all_stocks_data
        
        ldmReturn = [] # List of data matrixes to return
        for naDataLabel in all_stocks_data:
            ldmReturn.append( pa.DataFrame( naDataLabel, ts_list, symbol_list) )            

        
        ''' Contine to support single return type as a non-list '''
        if bStr:
            return ldmReturn[0]
        else:
            return ldmReturn            
        
        #get_data_hardread ends

    def get_data (self, ts_list, symbol_list, data_item, verbose=False, bIncDelist=False):
        '''
        Read data into a DataFrame, but check to see if it is in a cache first.
        @param ts_list: List of timestamps for which the data values are needed. Timestamps must be sorted.
        @param symbol_list: The list of symbols for which the data values are needed
        @param data_item: The data_item needed. Like open, close, volume etc.  May be a list, in which case a list of DataFrame is returned.
        @param bIncDelist: If true, delisted securities will be included.
        @note: If a symbol is not found then a message is printed. All the values in the column for that stock will be NaN. Execution then 
        continues as usual. No errors are raised at the moment.
        '''

        # Construct hash -- filename where data may be already
        #
        # The idea here is to create a filename from the arguments provided.
        # We then check to see if the filename exists already, meaning that
        # the data has already been created and we can just read that file.

        ls_syms_copy = copy.deepcopy(symbol_list)

        # Create the hash for the symbols
        hashsyms = 0
        for i in symbol_list:
            hashsyms = (hashsyms + hash(i)) % 10000000

        # Create the hash for the timestamps
        hashts = 0

        # print "test point 1: " + str(len(ts_list))
        # spyfile=os.environ['QSDATA'] + '/Processed/Norgate/Stocks/US/NYSE Arca/SPY.pkl'
        for i in ts_list:
            hashts = (hashts + hash(i)) % 10000000
        hashstr = 'qstk-' + str (self.source)+'-' +str(abs(hashsyms)) + '-' + str(abs(hashts)) \
            + '-' + str(hash(str(data_item))) #  + '-' + str(hash(str(os.path.getctime(spyfile))))

        # get the directory for scratch files from environment
        # try:
        #     scratchdir = os.environ['QSSCRATCH']
        # except KeyError:
        #     #self.rootdir = "/hzr71/research/QSData"
        #     raise KeyError("Please be sure to set the value for QSSCRATCH in config.sh or local.sh")

        # final complete filename
        cachefilename = self.scratchdir + '/' + hashstr + '.pkl'
        if verbose:
            print "cachefilename is: " + cachefilename

        # now eather read the pkl file, or do a hardread
        readfile = False  # indicate that we have not yet read the file

        #check if the cachestall variable is defined.
        # try:
        #     catchstall=dt.timedelta(hours=int(os.environ['CACHESTALLTIME']))
        # except:
        #     catchstall=dt.timedelta(hours=1)
        cachestall = dt.timedelta(hours=self.cachestalltime)

        # Check if the file is older than the cachestalltime
        if os.path.exists(cachefilename):
            if ((dt.datetime.now() - dt.datetime.fromtimestamp(os.path.getmtime(cachefilename))) < cachestall):
                if verbose:
                    print "cache hit"
                try:
                    cachefile = open(cachefilename, "rb")
                    start = time.time() # start timer
                    retval = pkl.load(cachefile)
                    elapsed = time.time() - start # end timer
                    readfile = True # remember success
                    cachefile.close()
                except IOError:
                    if verbose:
                        print "error reading cache: " + cachefilename
                        print "recovering..."
                except EOFError:
                    if verbose:
                        print "error reading cache: " + cachefilename
                        print "recovering..."
        if (readfile!=True):
            if verbose:
                print "cache miss"
                print "beginning hardread"
            start = time.time() # start timer
            if verbose:
                print "data_item(s): " + str(data_item)
                print "symbols to read: " + str(symbol_list)
            retval = self.get_data_hardread(ts_list, 
                symbol_list, data_item, verbose, bIncDelist)
            elapsed = time.time() - start # end timer
            if verbose:
                print "end hardread"
                print "saving to cache"
            try:
                cachefile = open(cachefilename,"wb")
                pkl.dump(retval, cachefile, -1)
                os.chmod(cachefilename,0666)
            except IOError:
                print "error writing cache: " + cachefilename
            if verbose:
                print "end saving to cache"
            if verbose:
                print "reading took " + str(elapsed) + " seconds"

        if type(retval) == type([]):
            for i, df_single in enumerate(retval):
                retval[i] = df_single.reindex(columns=ls_syms_copy)
        else:
            retval = retval.reindex(columns=ls_syms_copy)
        return retval

    def getPathOfFile(self, symbol_name, bDelisted=False):
        '''
        @summary: Since a given pkl file can exist in any of the folders- we need to look for it in each one until we find it. Thats what this function does.
        @return: Complete path to the pkl file including the file name and extension
        '''

        if not bDelisted:
            for path1 in self.folderList:
                if (os.path.exists(str(path1) + str(symbol_name + ".pkl"))):
                    # Yay! We found it!
                    return (str(str(path1) + str(symbol_name) + ".pkl"))
                    #if ends
                elif (os.path.exists(str(path1) + str(symbol_name + ".csv"))):
                    # Yay! We found it!
                    return (str(str(path1) + str(symbol_name) + ".csv"))
                #for ends

        else:
            ''' Special case for delisted securities '''
            lsPaths = []
            for sPath in self.folderList:
                if re.search('Delisted Securities', sPath) == None:
                    continue

                for sFile in dircache.listdir(sPath):
                    if not re.match( '%s-\d*.pkl'%symbol_name, sFile ) == None:
                        lsPaths.append(sPath + sFile)

            lsPaths.sort()
            return lsPaths

        print "Did not find path to " + str(symbol_name) + ". Looks like this file is missing"

    def getPathOfCSVFile(self, symbol_name):

        for path1 in self.folderList:
                if (os.path.exists(str(path1)+str(symbol_name+".csv"))):
                    # Yay! We found it!
                    return (str(str(path1)+str(symbol_name)+".csv"))
                    #if ends
                #for ends
        print "Did not find path to " + str (symbol_name)+". Looks like this file is missing"    

    def get_all_symbols (self):
        '''
        @summary: Returns a list of all the symbols located at any of the paths for this source. @see: {__init__}
        @attention: This will discard all files that are not of type pkl. ie. Only the files with an extension pkl will be reported.
        '''

        listOfStocks = list()
        #Path does not exist

        if (len(self.folderList) == 0):
            raise ValueError("DataAccess source not set")

        for path in self.folderList:
            stocksAtThisPath = list()
            #print str(path)
            stocksAtThisPath = dircache.listdir(str(path))
            #Next, throw away everything that is not a .pkl And these are our stocks!
            stocksAtThisPath = filter (lambda x:(str(x).find(str(self.fileExtensionToRemove)) > -1), stocksAtThisPath)
            #Now, we remove the .pkl to get the name of the stock
            stocksAtThisPath = map(lambda x:(x.partition(str(self.fileExtensionToRemove))[0]),stocksAtThisPath)

            listOfStocks.extend(stocksAtThisPath)
            #for stock in stocksAtThisPath:
                #listOfStocks.append(stock)
        return listOfStocks
        #get_all_symbols ends

    def check_symbol(self, symbol, s_list=None):
        '''
        @summary: Returns True if given symbol is present in the s_list.
        @param symbol: Symbol to be checked for.
        @param s_list: Optionally symbol sub-set listing can be given.
                        if not provided, all listings are searched.
        @return:  True if symbol is present in specified list, else False.
        '''
        
        all_symbols = list()
        
        # Create a super-set of symbols.
        if s_list is not None:
            all_symbols = self.get_symbols_from_list(s_list)
        else:
            all_symbols = self.get_all_symbols()
        
        # Check if the symbols is present.
        if ( symbol in all_symbols ):
            return True
        else:
            return False

    def get_symbols_from_list(self, s_list):
        ''' Reads all symbols from a list '''
        ls_symbols = []
        if (len(self.folderList) == 0):
            raise ValueError("DataAccess source not set")

        for path in self.folderList:
            path_to_look = path + 'Lists/' + s_list + '.txt'
            ffile = open(path_to_look, 'r')
            for f in ffile.readlines():
                j = f[:-1]
                ls_symbols.append(j)
            ffile.close()

        return ls_symbols

    def get_symbols_in_sublist (self, subdir):
        '''
        @summary: Returns all the symbols belonging to that subdir of the data store.
        @param subdir: Specifies which subdir you want.
        @return: A list of symbols belonging to that subdir
        '''

        pathtolook = self.rootdir + self.midPath + subdir
        stocksAtThisPath = dircache.listdir(pathtolook)

        #Next, throw away everything that is not a .pkl And these are our stocks!
        try:
            stocksAtThisPath = filter (lambda x:(str(x).find(str(self.fileExtensionToRemove)) > -1), stocksAtThisPath)
            #Now, we remove the .pkl to get the name of the stock
            stocksAtThisPath = map(lambda x:(x.partition(str(self.fileExtensionToRemove))[0]),stocksAtThisPath)
        except:
            print "error: no path to " + subdir
            stocksAtThisPath = list()

        return stocksAtThisPath
        #get_all_symbols_on_exchange ends

    def get_sublists(self):
        '''
        @summary: Returns a list of all the sublists for a data store.
        @return: A list of the valid sublists for the data store.
        '''

        return self.folderSubList
        #get_sublists

    def get_data_labels(self):
        '''
        @summary: Returns a list of all the data labels available for this type of data access object.
        @return: A list of label strings.
        '''

        if (self.source != DataSource.COMPUSTAT):
            print 'Function only valid for Compustat objects!'
            return []

        return DataItem.COMPUSTAT

        #get_data_labels

    def get_info(self):
        '''
        @summary: Returns and prints a string that describes the datastore.
        @return: A string.
        '''

        if (self.source == DataSource.NORGATE):
            retstr = "Norgate:\n"
            retstr = retstr + "Daily price and volume data from Norgate (premiumdata.net)\n"
            retstr = retstr + "that is valid at the time of NYSE close each trading day.\n"
            retstr = retstr + "\n"
            retstr = retstr + "Valid data items include: \n"
            retstr = retstr + "\topen, high, low, close, volume, actual_close\n"
            retstr = retstr + "\n"
            retstr = retstr + "Valid subdirs include: \n"
            for i in self.folderSubList:
                retstr = retstr + "\t" + i + "\n"

        elif (self.source == DataSource.YAHOO):
            retstr = "Yahoo:\n"
            retstr = retstr + "Attempts to load a custom data set, assuming each stock has\n"
            retstr = retstr + "a csv file with the name and first column as the stock ticker,\ date in second column, and data in following columns.\n"
            retstr = retstr + "everything should be located in QSDATA/Yahoo\n"
            for i in self.folderSubList:
                retstr = retstr + "\t" + i + "\n"

        elif (self.source == DataSource.COMPUSTAT):
            retstr = "Compustat:\n"
            retstr = retstr + "Compilation of (almost) all data items provided by Compustat\n"
            retstr = retstr + "Valid data items can be retrieved by calling get_data_labels(): \n"
            retstr = retstr + "\n"
            retstr = retstr + "Valid subdirs include: \n"
            for i in self.folderSubList:
                retstr = retstr + "\t" + i + "\n"
        elif (self.source == DataSource.CUSTOM):
            retstr = "Custom:\n"
            retstr = retstr + "Attempts to load a custom data set, assuming each stock has\n"
            retstr = retstr + "a csv file with the name and first column as the stock ticker, date in second column, and data in following columns.\n"
            retstr = retstr + "everything should be located in QSDATA/Processed/Custom\n"
        elif (self.source == DataSource.MLT):
            retstr = "ML4Trading:\n"
            retstr = retstr + "Attempts to load a custom data set, assuming each stock has\n"
            retstr = retstr + "a csv file with the name and first column as the stock ticker,\ date in second column, and data in following columns.\n"
            retstr = retstr + "everything should be located in QSDATA/Processed/ML4Trading\n"
        else:
            retstr = "DataAccess internal error\n"

        print retstr
        return retstr
        #get_sublists


    #class DataAccess ends
if __name__ == '__main__':
    # Setup DataAccess object
    c_dataobj = DataAccess('Yahoo')
    
    # Check if GOOG is a valid symbol.
    val = c_dataobj.check_symbol('GOOG')
    print "Is GOOG a valid symbol? :" , val
    
    # Check if QWERTY is a valid symbol.
    val = c_dataobj.check_symbol('QWERTY')
    print "Is QWERTY a valid symbol? :" , val

    # Check if EBAY is part of SP5002012 list.
    val = c_dataobj.check_symbol('EBAY', s_list='sp5002012')
    print "Is EBAY a valid symbol in SP5002012 list? :", val

    # Check if GLD is part of SP5002012 after checking if GLD is a valid symbol.
    val = c_dataobj.check_symbol('GLD')
    print "Is GLD a valid symbol? : ", val
    val = c_dataobj.check_symbol('GLD', 'sp5002012')
    print "Is GLD a valid symbol in sp5002012 list? :", val
