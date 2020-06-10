import urllib.request
import re
from bs4 import BeautifulSoup
from bs4.element import Tag

url = "https://pl.kingofsat.net/pos-{}E.php"

def extract_audio_pids( line ):
    p = re.compile(r'(\d+)(?:[\| ]([A-Za-z]+))?', re.IGNORECASE)
    m = p.findall(line)
    return m

class Service():
    def __init__(self, channel):
        if len(channel) != 14:
            raise Exception
        self.ServiceID = int( channel[7] )
        self.VPID = int( channel[8] )
        self.APIDS = extract_audio_pids(channel[9])
        self.PMTPID = int( channel[10] ) if channel[10] else None
        self.TeletextPID = int( channel[12] ) if channel[12] else None
        self.PCR = int(channel[11]) if channel[11] else None

class Kingofsat:
    def __init__(self, orbitalPositions):
        self.data = {}

        for orbitalPos in orbitalPositions:
            fullUrl = url.format(orbitalPos / 10)
            print("Connecting to {}".format(fullUrl))
            try:
                resp = urllib.request.urlopen(fullUrl)
                if not resp:
                    print("Connection to {} failed.".format(fullUrl))
                    exit(2)

                print("Parsing data...")
                soup = BeautifulSoup(resp.read(), 'html.parser')
                tables = soup.find_all('table', attrs={'class': 'fl'})
                data = []
                for table in tables:
                    rows = table.find_all('tr')
                    for row in rows:
                        cols = row.find_all('td')
                        channel = []
                        for t in cols:
                            channel.append(self.__getChildren(t))
                        try:
                            data.append(Service(channel))
                        except:
                            pass
                self.data[orbitalPos] = data
                print("Parsing complete.")
            except urllib.request.URLError as e:
                print("Parsing error: {}".format(e.reason))
                exit(2)

    def __getChildren(self, child):
        if type(child) is not Tag:
            return child.strip()
        if len(list(child.children)) == 0:
            if len(child.text) == 0:
                return None
            return child.text

        text = None
        for c in child.children:
            ret = self.__getChildren(c)
            if ret is not None and len(ret) != 0:
                if text is None:
                    text = ret
                else:
                    text = text + "|" + ret
        return text

    def findService(self, OrbitalPos, serviceID):
        return next((x for x in self.data[OrbitalPos] if x.ServiceID == serviceID), None )
