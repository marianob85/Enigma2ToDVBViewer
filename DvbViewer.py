import lameDB

class Channel:
    def __init__(self, lamedbService: lameDB.Service):
        self.TunerType = 1       # 1 - Sat, 2 - Terrestrial
        self.Root = None            # List tree name
        self.Category = None        # Category
        self.Name = lamedbService.ChannelName            # Channel name
        self.OrbitalPos = lamedbService.Transponder.Data.OrbitalPosition      # OrbitalPosition
        self.NetworkID = lamedbService.Transponder.OriginalNetworkID       # OriginalNetworkID
        self.StreamID = lamedbService.Transponder.TransportStreamID        # TransportStreamID
        self.SID = lamedbService.ServiceID             # Service ID
        #self.PMTPID = None
        #self.VPID = None
        #self.APID = None
        #self.PCRPID = None
        #self.AC3 = None
        #self.Language = None
        #self.Volume = None
        #self.EPGFlag = None
        #self.TelePID = None
        #self.AudioChannel = None
        self.Encrypted = 25     # ??
        #self.Group = None
        self.FEC = self.__fec(lamedbService.Transponder.Data.FEC)
        self.Frequency = self.__frequency(lamedbService.Transponder.Data.Frequency)       # Frequency
        self.Polarity = self.__polarity(lamedbService.Transponder.Data.Polarization)        # Polarization
        self.Symbolrate = self.__symbolrate(lamedbService.Transponder.Data.SymbolRateBPS)      # SymbolRateBPS
        self.SatModulation = self.__satmodulation(lamedbService.Transponder.Data.Modulation,
                                                  lamedbService.Transponder.Data.System,
                                                  lamedbService.Transponder.Data.Rolloff,
                                                  lamedbService.Transponder.Data.Pilot)   # Modulation & Rolloff & Pilot & System
        #self.SubStreamID = None

    def __fec(self, fec):
        # Enigma2
        # 0=None , 1=Auto, 2=1/2, 3=2/3, 4=3/4 5=5/6, 6=7/8, 7=3/5, 8=4/5, 9=8/9, 10=9/10.
        EnigmaMap = {}
        EnigmaMap["0"] = "-1"
        EnigmaMap["1"] = "-1"
        EnigmaMap["2"] = "0"
        EnigmaMap["3"] = "1"
        EnigmaMap["4"] = "2"
        EnigmaMap["5"] = "3"
        EnigmaMap["6"] = "4"
        EnigmaMap["7"] = "6"
        EnigmaMap["8"] = "7"
        EnigmaMap["9"] = "5"
        EnigmaMap["10"] = "8"

        return EnigmaMap[fec]

    def __frequency(self, frequency):
        return frequency // 1000

    def __polarity(self, polarity):
        if polarity == 0:
            return 'h'
        elif polarity == 1:
            return 'v'

        print("Polarity unknown: {0}".format(polarity))
        return None

    def __symbolrate(self, symbolrate):
        return symbolrate // 1000

    def __modulation(self, modulation):
        if modulation == 0:
            return 0
        elif modulation == 1:
            return 0b1
        elif  modulation == 2:
            return 0b11
        elif modulation == 3:
            return 0b10

        print("Modulation unknown: {0}".format(modulation))
        return None

    def __rolloff(self, rolloff):
        if rolloff is None:
            return 0b11
        else:
            return rolloff & 0b11

    def __pilot(self, pilot):
        if pilot == 0:
            return 0
        elif pilot == 1:
            return 0
        elif pilot == 2:
            return 1

        print("Pilot unknown: {0}".format( pilot ))
        return None

    def __satmodulation(self, modulation, system, rolloff, pilot):
        satModulation = self.__modulation(modulation)
        satModulation |= ( system & 1 ) << 2
        satModulation |= self.__rolloff(rolloff) << 3
        satModulation |= self.__pilot(pilot) << 7

        return satModulation


class DvbViewer():
    def __init__(self, rootname):
        self.Channels = []
        self.rootname = rootname

    def addservice(self, service: lameDB.Service, name):
        channel = Channel(service)
        channel.Root = self.rootname
        channel.Category = name
        self.Channels.append(channel)
        return

    def save(self, filename):
        file = open( filename,  encoding='utf-8', mode="w")

        channelCount = 0
        for channel in self.Channels:
            file.write('[Channel{0}]\n'.format(channelCount))
            for v,k in channel.__dict__.items():
                file.write('{0}={1}\n'.format(v,k))
            file.write('\n')
            channelCount = channelCount + 1
        file.close()
