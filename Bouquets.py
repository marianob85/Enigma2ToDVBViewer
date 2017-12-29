#===============================================================================
# Author: Mariusz Brzeski 
# Date 01.02.2014
#===============================================================================
import os
import subprocess
import shutil
import re
import sys
import fileinput
import codecs

class CService():
    def __init__(self):
        self.ServiceID = None
        self.TransportStreamID = None
        self.OriginalNetworkID = None
        self.DVBNameSpace = None

class  CBouquet():
    def __init__(self):
        self.Name = None
        self.Services = []

class CBouquets():   
    def Read(self, FileName ):
        
        cBouquets = []
        
        with codecs.open( FileName, 'r', encoding='utf-8',  errors='ignore'  ) as f:
            for Line in f:
                Bouquet = re.match( '^#SERVICE:.*[\d:]{10}([\d\w\.]+)', Line )
                if Bouquet == None:
                    Bouquet = re.match( '^#SERVICE [\d:]+FROM BOUQUET "([\d\w\.]+)"', Line )
                if Bouquet:
                    FileName = os.path.dirname( FileName )
                    FileName = os.path.join( FileName, Bouquet.group(1) )
                    cBouquet = self.ReadBouquet( FileName )
                    if cBouquet.Name == None:
                        continue
                    
                    cBouquets.append( cBouquet )
        return cBouquets
                                         
        
    def ReadBouquet(self, FilePath):
        
        cBouquet = CBouquet()
        
        with codecs.open( FilePath, 'r', encoding='utf-8', errors='ignore' ) as f:       
            for Line in f:
                Name = re.match( '^#NAME (.+)$', Line )
                if Name:
                   cBouquet.Name = Name.group( 1 ).encode('utf-8', 'ignore').strip()

                   continue
                    
                # Co oznacza 1:0:1 i dlaczego dla niektorych jest 19 ? Moze pilot...
                Service = re.match( '^#SERVICE 1:0:\d+:([\d\w\+]+):([\d\w]+):([\d\w]+):([\d\w]+):0:0:0:', Line )
                if Service:
                    cService = CService()
                    cService.ServiceID = int( Service.group(1) , 16)
                    cService.TransportStreamID = int( Service.group(2) , 16)
                    cService.OriginalNetworkID = int( Service.group(3) , 16)
                    cService.DVBNameSpace = int( Service.group(4) , 16)
                    
                    cBouquet.Services.append(cService)
        return cBouquet
    
    
    
    
    