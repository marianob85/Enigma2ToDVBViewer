#===============================================================================
# Author: Mariusz Brzeski 
# Date 01.02.2012
#===============================================================================
import os
import subprocess
import shutil
import re
import sys
import fileinput
import Bouquets
import codecs
from optparse import OptionParser


class CDvbViewerIni():
    def __init__(self):
        self.ChannelS = {}
    
    def Read(self, Line):
        Data = re.match( '^([\d\w-]+)=([\d\w\s-]+)', Line )
        if Data:
            self.ChannelS[ Data.group( 1 ) ] = Data.group(2).strip()
    
class CDvbViewerIniCol():
    def __init__(self):
          self.Channels = []
        
    def ReadFile(self, FileName ):
        with open( FileName ) as f:
            cDvbViewerIni = None
            for Line in f:
                Channel = re.match( '^\[\w+\d+\]', Line )
                if Channel:
                    #save Last
                    if cDvbViewerIni:
                        self.Channels.append( cDvbViewerIni )
                    cDvbViewerIni = CDvbViewerIni()
                    continue
                cDvbViewerIni.Read(Line)
            self.Channels.append( cDvbViewerIni )
    
    def Find(self, Frequency, Polarization, ServiceID, TransportStreamID, OriginalNetworkID, OrbitalPosition ):
        for cDvbIni in self.Channels:
            if cDvbIni.ChannelS["Polarity"] == Polarization and int( cDvbIni.ChannelS["SID"] ) == ServiceID and int( cDvbIni.ChannelS["StreamID"] ) == TransportStreamID and int( cDvbIni.ChannelS["OrbitalPos"] ) == OrbitalPosition:
                return cDvbIni
        return None
class CTransponderS():
    def __init__ (self ):
        self.Frequency = 0x0          # In Hertz
        self.SymbolRateBPS = 0x0      # Symbol rate in bits per second.
        self.Polarization = 0x0       # 0=Horizontal, 1=Vertical, 2=Circular Left, 3=Circular right.
        self.FEC = ''                 # 0=None , 1=Auto, 2=1/2, 3=2/3, 4=3/4 5=5/6, 6=7/8, 7=3/5, 8=4/5, 9=8/9, 10=9/10.
        self.OrbitalPosition = 0x0    # in degrees East: 130 is 13.0E, 192 is 19.2E. Negative values are West -123 is 12.3West. 
        self.Inversion = 0x0          # 0=Auto, 1=On, 2=Off
        self.Flags = 0x0              # Flags (Only in version 4): Field is absent in version 3.
        self.System = 0x0             # 0=DVB-S 1=DVB-S2.
        self.Modulation = 0x0         # 0=Auto, 1=QPSK, 2=QAM16, 3=8PSK
        self.Rolloff = 0x0            # (Only used in DVB-S2): 0=0.35, 1=0.25, 3=0.20
        self.Pilot = 0x0              # (Only used in DVB-S2): 0=Auto, 1=Off, 1=On.
    
    def ReadData(self, Line ):
        DataLine = Line.split( ":")
        
        if DataLine:
            try:
                self.Frequency = int( DataLine[0] ) 
                self.SymbolRateBPS = int( DataLine[1] )
                self.Polarization = int( DataLine[2] )
                self.FEC = DataLine[3]
                self.OrbitalPosition = int( DataLine[4] )
                self.Inversion = int( DataLine[5] )
                self.Flags = int( DataLine[6] )
                self.System = int( DataLine[7] )
                self.Modulation = int( DataLine[8] )
                self.Rolloff = int( DataLine[9] )
                self.Pilot = int( DataLine[10] )
            except IndexError:
                return
        else:
            raise
    
    def PolarizationS(self):
        if self.Polarization == 0:
            return 'h'
        if self.Polarization == 1:
            return 'v'
    
    def ModulationS(self):
        if self.Modulation == 1:
            return 1
        elif self.Modulation == 3:
            return 6
        elif self.System == 0:
            return 0
        elif self.System == 1:
            return 4
        return 0
    
    def FecS(self):
        # TransEdit ini
            # 0  - auto
        
        # Enigma2
        # 0=None , 1=Auto, 2=1/2, 3=2/3, 4=3/4 5=5/6, 6=7/8, 7=3/5, 8=4/5, 9=8/9, 10=9/10.
        EnigmaMap = {}
        EnigmaMap[ "0" ] = "-1"
        EnigmaMap[ "1" ] = "-1"
        EnigmaMap[ "2" ] = "0"
        EnigmaMap[ "3" ] = "1"
        EnigmaMap[ "4" ] = "2"
        EnigmaMap[ "5" ] = "3"
        EnigmaMap[ "6" ] = "4"
        EnigmaMap[ "7" ] = "6"
        EnigmaMap[ "8" ] = "7"
        EnigmaMap[ "9" ] = "5"
        EnigmaMap[ "10" ] = "8"
        
        return EnigmaMap[self.FEC]
    
class CTransponder():
    def __init__ (self ):
        self.DVBNameSpace = 0x0
        self.TransportStreamID = 0x0
        self.OriginalNetworkID = 0x0
        self.Type = ''        # Satellite DVB ( s ), Terestrial DVB ( t ), Cable DVB ( c )
        self.Data = None
    
    def ReadHeader(self, Line ):
        HeaderLine = re.match(r"([\d\w]+):([\d\w]+):([\d\w]+)", Line )
        if HeaderLine:
            self.DVBNameSpace = int( HeaderLine.group(1) , 16) 
            self.TransportStreamID = int( HeaderLine.group(2) , 16)
            self.OriginalNetworkID = int( HeaderLine.group(3) , 16)
        else:
            raise
        
    def ReadData(self, Line ):
        DataLine = re.match(r"([stc]) ([\d\w:]+)", Line )
        if DataLine:
             self.Type = DataLine.group(1)
             if self.Type == 's':
                 self.Data = CTransponderS()
                 self.Data.ReadData( DataLine.group(2) ) 
            

class CService():
    def __init__(self):
        self.ServiceID = 0x0
        self.ServiceType = 0x0
        self.ServiceNumber = 0x0
        self.Transponder = None
        self.ChannelName = None
        self.Provider = None
        
    def ReadData(self, Line ):
        DataLine = Line.split( ":")
        
        if DataLine:
            try:
                 self.ServiceID = int( DataLine[0] , 16)
                 self.ServiceType = int( DataLine[4] , 16)
                 self.ServiceNumber = int( DataLine[5] , 16)   
            except IndexError:
                return None, None, None
        return int( DataLine[1] , 16), int( DataLine[2] , 16), int( DataLine[3] , 16)

    def ReadChannelName(self, Line ):
        self.ChannelName = Line.strip()
        
    def ReadProvider(self, Line ):
        self.Provider = Line
        
class CEnigma2Struct():
    def __init__ (self, Path ):
        if  Path==None:
            return
        self.Transponders = []
        self.Services = []
        self.Open( Path )
        
    def Open(self, Path ):
        self._file = open( Path, 'r')
        self._read()
           
    def _read(self):
        self._checkheader()
        self._readTranspondersSection()
        self._readServiceSection()
        
    def _checkheader(self):
        HeaderLine = re.match(r"eDVB services /(4)/",  self._file.readline())
       
        if HeaderLine:
            self._version = HeaderLine.group(1)
        else:
            raise
        
    def _readTranspondersSection(self):
        transpondersLine = self._file.readline().strip()
        if transpondersLine != 'transponders':
            raise
        
        while True:
            Line = self._file.readline().strip()
            if Line == 'end':
                break       
                     
            cTransponder = CTransponder()
            cTransponder.ReadHeader( Line )
            cTransponder.ReadData( self._file.readline().strip() )
            
            self.Transponders.append( cTransponder )
            
            if self._file.readline().strip() != '/':
                raise
                         
    def _readServiceSection(self):
        transpondersLine = self._file.readline().strip()
        if transpondersLine != 'services':
            raise
        
        while True:
            Line = self._file.readline().strip()
            if Line == 'end':
                break 
        
            cService = CService() 
            DVBNameSpace, TransportStreamID, OriginalNetworkID = cService.ReadData( Line )
            
            cService.ReadChannelName( self._file.readline().strip() )
            cService.ReadProvider( self._file.readline().strip() )
            
            for Transponder in self.Transponders:
                if Transponder.DVBNameSpace == DVBNameSpace and Transponder.TransportStreamID == TransportStreamID and Transponder.OriginalNetworkID == OriginalNetworkID:
                    cService.Transponder = Transponder
                    break
            
            if cService.Transponder == None:
                print "Can't find tranponder" 
            self.Services.append( cService )
        return   
    
    def FindService(self, ServiceID, TransportStreamID, OriginalNetworkID, DVBNameSpace ):
        for Service in self.Services:
            if Service.ServiceID == ServiceID and Service.Transponder.DVBNameSpace == DVBNameSpace and Service.Transponder.TransportStreamID == TransportStreamID and Service.Transponder.OriginalNetworkID == OriginalNetworkID:
                return Service
        return None


if __name__ == '__main__':
    
    parser = OptionParser()
    
    parser.add_option("-r", "--root", 
                      action="store",
                      type="string",
                      dest="RootName",
                      help="DVBViewer list root name")
    parser.add_option("-l", "--lameDB",
                      action="store",
                      type="string",
                      dest="LameDBile",
                      help="Enigma 2 files list: path to lamedb file")
    parser.add_option("-o", "--out",
                      action="store",
                      type="string",
                      dest="OutputFileList",
                      help="DVBViewer output ini file")
    parser.add_option("-t", "--transponders",
                      action="append",
                      type="string",
                      dest="TransponderListFiles",
                      help="DVBViewer transponder lists file")
    
    (options, args) = parser.parse_args()
    
    cEnigma2Struct = CEnigma2Struct( options.LameDBile )
    
    cBouquetPath = os.path.dirname( options.LameDBile )
    cBouquetPath = os.path.join(cBouquetPath, "bouquets.tv" )
    
    cBouquets = Bouquets.CBouquets()
    cBouquetsList = cBouquets.Read( cBouquetPath )
    
    cDvbViewerIniCol = CDvbViewerIniCol()
    
    for i in options.TransponderListFiles:
        cDvbViewerIniCol.ReadFile( i )
    
    file = open( options.OutputFileList, 'w')
    Channel = 0
    
    for cBouquet in cBouquetsList:
        for cBouquetService in cBouquet.Services:
            cService = cEnigma2Struct.FindService(cBouquetService.ServiceID, cBouquetService.TransportStreamID, cBouquetService.OriginalNetworkID, cBouquetService.DVBNameSpace)
            if cService == None:
                print "Can't find serviceID: " + cBouquetService.ServiceID
                exit( 0 )
            
            cDvbViewerIni = cDvbViewerIniCol.Find( cService.Transponder.Data.Frequency / 1000,
                                   cService.Transponder.Data.PolarizationS(),
                                   cService.ServiceID,
                                   cService.Transponder.TransportStreamID,
                                   cService.Transponder.OriginalNetworkID,
                                   cService.Transponder.Data.OrbitalPosition )
            
            if cDvbViewerIni == None:
                print "Can't find: {0}".format( cService.ChannelName )             
                continue
            
            cDvbViewerIni.ChannelS[ "Root" ] = options.RootName
            cDvbViewerIni.ChannelS[ "Category" ] = cBouquet.Name
            cDvbViewerIni.ChannelS[ "Name" ] = cService.ChannelName
            
            file.write( '[Channel{0}]\n'.format( Channel ) )
            for k,v in cDvbViewerIni.ChannelS.iteritems():  
                file.write( '{0}={1}'.format(k,v).strip() )
                file.write( '\n' )
            file.write( "\n")    
            Channel= Channel + 1  
    exit( 0 )
    
    # 08
