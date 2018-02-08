import urllib2
response = urllib2.urlopen('https://planning.univ-lorraine.fr/jsp/custom/modules/plannings/anonymous_cal.jsp?resources=94695&projectId=5&calType=ical&nbWeeks=16')
html = response.read()

print("%s", html)
