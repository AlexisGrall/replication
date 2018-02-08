import urllib2
DEFAULT_URL = 'https://planning.univ-lorraine.fr/jsp/custom/modules/plannings/anonymous_cal.jsp?resources=94695&projectId=5&calType=ical&irstDate=2018-02-05&lastDate=2018-02-11'

def getFromUrl(url=DEFAULT_URL):
    response = urllib2.urlopen(url)
    return response
