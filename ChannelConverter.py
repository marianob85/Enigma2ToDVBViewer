#===============================================================================
# Author: Mariusz Brzeski 
# Date 01.02.2012
#===============================================================================
import os
import subprocess
import shutil
import sys
import fileinput
import codecs
import lameDB
import lameDBBouquet
import DvbViewer

from optparse import OptionParser

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

    (options, args) = parser.parse_args()
    
    cEnigma2Struct = lameDB.Enigma2Struct( options.LameDBile )
    
    cBouquetPath = os.path.dirname( options.LameDBile )
    cBouquetPath = os.path.join(cBouquetPath, "bouquets.tv" )
    
    cBouquets = lameDBBouquet.Bouquets()
    cBouquetsList = cBouquets.Read( cBouquetPath )

    dvbViewer = DvbViewer.DvbViewer(options.RootName)

    for bouquet in cBouquetsList:
        for bouquetService in bouquet.Services:
            service = cEnigma2Struct.FindService(bouquetService)
            if service == None:
                print ("Can't find serviceID: " + bouquetService.ServiceID)
                exit( 0 )

            dvbViewer.addservice(service, bouquet.Name)

    dvbViewer.save(options.OutputFileList)