import lameDB
import Kingofsat

LOF_SW = 11700
LOF_1 = 9750
LOF_2 = 10600


class Channel:
    def __init__(self, lamedbService: lameDB.Service, kingofsat: Kingofsat.Service, kofAudioID):
        self.TunerType = 1  # 1 - Sat, 2 - Terrestrial
        self.Root = None  # List tree name
        self.Category = None  # Category
        self.Name = lamedbService.ChannelName  # Channel name
        self.OrbitalPos = lamedbService.Transponder.Data.OrbitalPosition  # OrbitalPosition
        self.NetworkID = lamedbService.Transponder.OriginalNetworkID  # OriginalNetworkID
        self.StreamID = lamedbService.Transponder.TransportStreamID  # TransportStreamID
        self.SID = lamedbService.ServiceID  # Service ID
        self.Encrypted = 25  # ??
        self.FEC = self.__fec(lamedbService.Transponder.Data.FEC)
        self.Frequency = self.__frequency(lamedbService.Transponder.Data.Frequency)  # Frequency
        self.Polarity = self.__polarity(lamedbService.Transponder.Data.Polarization)  # Polarization
        self.Symbolrate = self.__symbolrate(lamedbService.Transponder.Data.SymbolRateBPS)  # SymbolRateBPS
        self.SatModulation = self.__satmodulation(lamedbService.Transponder.Data.Modulation,
                                                  lamedbService.Transponder.Data.System,
                                                  lamedbService.Transponder.Data.Rolloff,
                                                  lamedbService.Transponder.Data.Pilot)  # Modulation & Rolloff & Pilot & System
        self.LNB = self.__lnb(self.__frequency(lamedbService.Transponder.Data.Frequency))
        self.LNBSelection = self.__lnb_selection(self.__frequency(lamedbService.Transponder.Data.Frequency))
        self.SubStreamID = None
        self.AC3 = None
        self.Group = None
        self.Volume = None
        self.EPGFlag = None
        self.AudioChannel = None
        if kingofsat:
            self.PMTPID = kingofsat.PMTPID
            self.VPID = kingofsat.VPID
            self.APID = kofAudioID[0]
            self.PCRPID = kingofsat.PCR
            self.Language = kofAudioID[1] if len(kofAudioID[1]) > 0 else str(kofAudioID[0])
            self.TelePID = kingofsat.TeletextPID
            if kofAudioID != kingofsat.APIDS[0]:
                self.Name = "{} ({})".format(self.Name, self.Language)
                self.Encrypted = self.Encrypted | 0B10000000

    def __lnb(self, frequency):
        if frequency < LOF_SW:
            return LOF_1
        else:
            return LOF_2

    def __lnb_selection(self, frequency):
        if frequency < LOF_SW:
            return 0
        else:
            return 1

    def __fec(self, fec):
        EnigmaMap = {}
        EnigmaMap["0"] = "-1"
        EnigmaMap["1"] = "0"
        EnigmaMap["2"] = "1"
        EnigmaMap["3"] = "2"
        EnigmaMap["4"] = "3"
        EnigmaMap["5"] = "4"
        EnigmaMap["6"] = "6"
        EnigmaMap["7"] = "7"
        EnigmaMap["8"] = "5"
        EnigmaMap["9"] = "8"
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

        print("Pilot unknown: {0}".format(pilot))
        return None

    def __satmodulation(self, modulation, system, rolloff, pilot):
        satModulation = modulation  # DVBViewer: 00 = Auto, 01 = QPSK, 10 = 8PSK, 11 = 16QAM
        satModulation |= (system & 1) << 2
        satModulation |= self.__rolloff(rolloff) << 3
        satModulation |= self.__pilot(pilot) << 7

        return satModulation


class DvbViewer():
    def __init__(self, rootname):
        self.Channels = []
        self.rootname = rootname

    def addservice(self, service: lameDB.Service, kingofsat: Kingofsat.Service, name):
        if kingofsat:
            # For each audio id create new dvbViewer channel
            for audio in kingofsat.APIDS:
                self.__addchannel(service, kingofsat, name, audio)
        else:
            self.__addchannel(service, None, name, None)

    def __addchannel(self, service: lameDB.Service, kof: Kingofsat.Service, name, kofAudioID):
        channel = Channel(service, kof, kofAudioID)
        channel.Root = self.rootname
        channel.Category = name
        self.Channels.append(channel)

    def save(self, filename):
        file = open(filename, encoding='utf-8', mode="w")

        keyMap = {"LNBSelection": "LNB-Selection"}

        channelCount = 0
        for channel in self.Channels:
            file.write('[Channel{0}]\n'.format(channelCount))
            for v, k in channel.__dict__.items():
                if k is None:
                    continue
                if v in keyMap:
                    file.write('{0}={1}\n'.format(keyMap[v], k))
                else:
                    file.write('{0}={1}\n'.format(v, k))
            file.write('\n')
            channelCount = channelCount + 1
        file.close()
