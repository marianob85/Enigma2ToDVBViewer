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

class Service():
    def __init__(self):
        self.ServiceID = None
        self.TransportStreamID = None
        self.OriginalNetworkID = None
        self.DVBNameSpace = None

class Bouquet():
    def __init__(self):
        self.Name = None
        self.Services = []

class Bouquets():
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
        
        cBouquet = Bouquet()
        
        with codecs.open( FilePath, 'r', encoding='utf-8', errors='ignore' ) as f:       
            for Line in f:
                Name = re.match( '^#NAME (.+)$', Line )
                if Name:
                   cBouquet.Name = Name.group( 1 ).strip()

                   continue
                    
                # Co oznacza 1:0:1 i dlaczego dla niektorych jest 19 ? Moze pilot...
                serviceMath = re.match( '^#SERVICE 1:0:[\d\w]+:([\d\w\+]+):([\d\w]+):([\d\w]+):([\d\w]+):0:0:0:', Line )
                if serviceMath:
                    service = Service()
                    service.ServiceID = int( serviceMath.group(1) , 16)
                    service.TransportStreamID = int( serviceMath.group(2) , 16)
                    service.OriginalNetworkID = int( serviceMath.group(3) , 16)
                    service.DVBNameSpace = int( serviceMath.group(4) , 16)
                    
                    cBouquet.Services.append(service)
        return cBouquet
    
    
    
    
    