# ===============================================================================
# Author: Mariusz Brzeski
# Date 01.02.2012
# ===============================================================================
import os
import shutil
import pathlib
import lameDB
import lameDBBouquet

from optparse import OptionParser

# 0 : is a default value and it is always equal to 1
# 1 : this is also a default value, and it is always equal to 0
# 2 : service type:
# 3 : service Id
# 4: Trasponder Id
# 5 : NId, Network Id
# 6 : Namespace
# 7 : default value, always = 0
# 8 : default value, always = 0
# 9 : default value, always = 0

def getLogoName( lamedbService: lameDB.Service, bouquetService : lameDBBouquet.Service ):
    return "1_0_{:X}_{:X}_{:X}_{:X}_{:X}_0_0_0".format( bouquetService.ServiceType,
                                               lamedbService.ServiceID,
                                               lamedbService.Transponder.TransportStreamID,
                                               lamedbService.Transponder.OriginalNetworkID,
                                               lamedbService.Transponder.DVBNameSpace)


if __name__ == '__main__':
    parser = OptionParser()

    parser.add_option("-l", "--lameDB",
                      action="store",
                      type="string",
                      dest="LameDBile",
                      help="Enigma 2 files list: path to lamedb file")
    parser.add_option("-i", "--inDirectory",
                      action="store",
                      type="string",
                      dest="LogoInputDirectory",
                      help="Enigma2 logo input directory")

    parser.add_option("-o", "--outDirectory",
                      action="store",
                      type="string",
                      dest="LogoOutputDirectory",
                      help="DVBViewer output logos")

    (options, args) = parser.parse_args()

    cEnigma2Struct = lameDB.Enigma2Struct(options.LameDBile)

    cBouquetPath = os.path.dirname(options.LameDBile)
    cBouquetPath = os.path.join(cBouquetPath, "bouquets.tv")

    cBouquets = lameDBBouquet.Bouquets()
    cBouquetsList = cBouquets.Read(cBouquetPath)

    pathlib.Path(options.LogoOutputDirectory).mkdir(parents=True, exist_ok=True)

    inputDirectoryLogoList = [p for p in os.scandir(options.LogoInputDirectory) if p.is_file()]

    for bouquet in cBouquetsList:
        for bouquetService in bouquet.Services:
            service = cEnigma2Struct.FindService(bouquetService)
            if service is None:
                print("Can't find serviceID: " + bouquetService.ServiceID)
                exit(0)
            logoToFind = getLogoName(service, bouquetService);
            logos = [x for x in inputDirectoryLogoList if logoToFind.casefold() in x.name.casefold() ]
            if not logos:
                print("Can't find logo: {}: {} ".format(service.ChannelName, logoToFind))
                continue
            for file in logos:
                newName = file.name.replace(logoToFind, service.ChannelName ).replace(" ","")
                shutil.copy2(file.path, os.path.join(options.LogoOutputDirectory,newName) )
