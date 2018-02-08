from event import Event
import dl

def parseEvent(c):
    l = c.readline().strip().split(':')
    e = Event()
    while not (len(l) >= 2 and l[0] == "END" and l[1] == "VEVENT"):
        if (len(l) >= 1):         
            if (l[0] == "DTSTART"):
                e.dateStart = l[1]
            if (l[0] == "DTEND"):
                e.dateEnd = l[1]
            if (l[0] == "SUMMARY"):
                e.summary = l[1]
            if (l[0] == "LOCATION"):
                e.location = l[1]
            if (l[0] == "LAST-MODIFIED"):
                e.lastModified = l[1]
            if (l[0] == "UID"):
                e.uid = l[1]
        l = c.readline().strip().split(':')
    return e

def parser(calendar):
    eventLst = []
    line = calendar.readline()
    while not (line == ""):
        l =  line.strip().split(":")
        if (len(l) >= 2 and "BEGIN" == l[0] and "VEVENT" == l[1]):
            e = parseEvent(calendar)
            eventLst.append(e)
        line = calendar.readline()
    return eventLst

def parse(url=dl.DEFAULT_URL):
    eventLst = parser(dl.getFromUrl(url))
    return eventLst


for e in parse():
    print e.uid + "\t" + e.lastModified + "\t" + e.summary 



