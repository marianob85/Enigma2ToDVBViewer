# ===============================================================================
# Author: Mariusz Brzeski 
# Date 01.02.2012
# ===============================================================================
import os
import lameDB
import lameDBBouquet
import DvbViewer
import Kingofsat

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
    parser.add_option("-s",
                      action="store_true",
                      dest="Site",
                      help="Get additional data from kingofsat.net")

    (options, args) = parser.parse_args()

    cEnigma2Struct = lameDB.Enigma2Struct(options.LameDBile)

    cBouquetPath = os.path.dirname(options.LameDBile)
    cBouquetPath = os.path.join(cBouquetPath, "bouquets.tv")

    cBouquets = lameDBBouquet.Bouquets()
    cBouquetsList = cBouquets.Read(cBouquetPath)

    dvbViewer = DvbViewer.DvbViewer(options.RootName)

    kingOfSatData = None
    if options.Site:
        kingOfSatData = Kingofsat.Kingofsat(cEnigma2Struct.getOrbitals())

    for bouquet in cBouquetsList:
        for bouquetService in bouquet.Services:
            service = cEnigma2Struct.FindService(bouquetService)
            if service is None:
                print("Can't find serviceID: " + bouquetService.ServiceID)
                exit(0)

            kosService = None
            if kingOfSatData:
                kosService = kingOfSatData.findService(service.Transponder.Data.OrbitalPosition, service.ServiceID)

            dvbViewer.addservice(service, kosService, bouquet.Name)

    dvbViewer.save(options.OutputFileList)
