import re
import lameDBBouquet

class TransponderS():
    def __init__(self):
        self.Frequency = 0x0  # In Hertz
        self.SymbolRateBPS = 0x0  # Symbol rate in bits per second.
        self.Polarization = 0x0  # 0=Horizontal, 1=Vertical, 2=Circular Left, 3=Circular right.
        self.FEC = ''  # 0=None , 1=Auto, 2=1/2, 3=2/3, 4=3/4 5=5/6, 6=7/8, 7=3/5, 8=4/5, 9=8/9, 10=9/10.
        self.OrbitalPosition = 0x0  # in degrees East: 130 is 13.0E, 192 is 19.2E. Negative values are West -123 is 12.3West.
        self.Inversion = 0x0  # 0=Auto, 1=On, 2=Off
        self.Flags = 0x0  # Flags (Only in version 4): Field is absent in version 3.
        self.System = 0x0  # 0=DVB-S 1=DVB-S2.
        self.Modulation = 0x0  # 0=Auto, 1=QPSK, 2=QAM16, 3=8PSK
        self.Rolloff = 0x0  # (Only used in DVB-S2): 0=0.35, 1=0.25, 2=0.20
        self.Pilot = 0x0  # (Only used in DVB-S2): 0=Auto, 1=Off, 1=On.

    def ReadData(self, Line):
        DataLine = Line.split(":")

        if DataLine:
            try:
                self.Frequency = int(DataLine[0])
                self.SymbolRateBPS = int(DataLine[1])
                self.Polarization = int(DataLine[2])
                self.FEC = DataLine[3]
                self.OrbitalPosition = int(DataLine[4])
                self.Inversion = int(DataLine[5])
                self.Flags = int(DataLine[6])
                self.System = int(DataLine[7])
                self.Modulation = int(DataLine[8])
                self.Rolloff = int(DataLine[9])
                self.Pilot = int(DataLine[10])
            except IndexError:
                return
        else:
            raise




class Transponder():
    def __init__(self):
        self.DVBNameSpace = 0x0
        self.TransportStreamID = 0x0
        self.OriginalNetworkID = 0x0
        self.Type = ''  # Satellite DVB ( s ), Terestrial DVB ( t ), Cable DVB ( c )
        self.Data = None

    def ReadHeader(self, Line):
        HeaderLine = re.match(r"([\d\w]+):([\d\w]+):([\d\w]+)", Line)
        if HeaderLine:
            self.DVBNameSpace = int(HeaderLine.group(1), 16)
            self.TransportStreamID = int(HeaderLine.group(2), 16)
            self.OriginalNetworkID = int(HeaderLine.group(3), 16)
        else:
            raise

    def ReadData(self, Line):
        DataLine = re.match(r"([stc]) ([\d\w:]+)", Line)
        if DataLine:
            self.Type = DataLine.group(1)
            if self.Type == 's':
                self.Data = TransponderS()
                self.Data.ReadData(DataLine.group(2))


class Service():
    def __init__(self):
        self.ServiceID = 0x0
        self.ServiceType = 0x0
        self.ServiceNumber = 0x0
        self.Transponder = None
        self.ChannelName = None
        self.Provider = None

    def ReadData(self, Line):
        DataLine = Line.split(":")

        if DataLine:
            try:
                self.ServiceID = int(DataLine[0], 16)
                self.ServiceType = int(DataLine[4], 16)
                self.ServiceNumber = int(DataLine[5], 16)
            except IndexError:
                return None, None, None
        return int(DataLine[1], 16), int(DataLine[2], 16), int(DataLine[3], 16)

    def ReadChannelName(self, Line):
        self.ChannelName = Line.strip()

    def ReadProvider(self, Line):
        self.Provider = Line


class Enigma2Struct():
    def __init__(self, Path):
        if Path == None:
            return
        self.Transponders = []
        self.Services = []
        self.Open(Path)

    def Open(self, Path):
        self._file = open(Path, encoding='utf-8', mode="r")
        self._read()

    def _read(self):
        self._checkheader()
        self._readTranspondersSection()
        self._readServiceSection()

    def _checkheader(self):
        HeaderLine = re.match(r"eDVB services /(4)/", self._file.readline())

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

            transponder = Transponder()
            transponder.ReadHeader(Line)
            transponder.ReadData(self._file.readline().strip())

            self.Transponders.append(transponder)

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

            service = Service()
            DVBNameSpace, TransportStreamID, OriginalNetworkID = service.ReadData(Line)

            service.ReadChannelName(self._file.readline().strip())
            service.ReadProvider(self._file.readline().strip())

            for transponder in self.Transponders:
                if transponder.DVBNameSpace == DVBNameSpace and transponder.TransportStreamID == TransportStreamID and transponder.OriginalNetworkID == OriginalNetworkID:
                    service.Transponder = transponder
                    break

            if service.Transponder == None:
                print("Can't find tranponder")
            self.Services.append(service)
        return

    def FindService(self, bouquet : lameDBBouquet.Service):
        for service in self.Services:
            if service.ServiceID == bouquet.ServiceID and service.Transponder.DVBNameSpace == bouquet.DVBNameSpace and service.Transponder.TransportStreamID == bouquet.TransportStreamID and service.Transponder.OriginalNetworkID == bouquet.OriginalNetworkID:
                return service
        return None

