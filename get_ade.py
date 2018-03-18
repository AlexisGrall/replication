from icalendar import Calendar, Event
import os
import urllib2

# default url for ade calendar
DEFAULT_URL = 'https://planning.univ-lorraine.fr/jsp/custom/modules/plannings/anonymous_cal.jsp?resources=94694,94695,137604,137605,143847,161667,131172,28064,180436,180437,187172,187173,188343,189790,190400,191558,195038,195039,195267,196054,196183,196296,206014,206831,207691,223135,223136,224368,229624,231294,234516&projectId=5&calType=ical&firstDate=2018-03-12&lastDate=2018-03-18'

URL_FILE = "url.txt"

# file in which the last icalendar was written
ICS_FILE = 'ade.ics'
# icalendar keys we do not update in google calendar
NOT_UPDATED_KEYS = ["UID", "DTSTAMP", "CREATED", "LAST-MODIFIED", "SEQUENCE"]
DATE_KEYS = ["DTSTAMP", "CREATED", "LAST-MODIFIED", "DTSTART", "DTEND"]

def get_from_url(url=DEFAULT_URL):
    response = urllib2.urlopen(url)
    return response

def get_ade_cal(url=DEFAULT_URL):
    response = get_from_url(url).read()
    ade_cal = Calendar.from_ical(response)
    return ade_cal

def event_equals(e1, e2):
    ''' Returns true if the events have the same ids
    '''
    return e1['UID'] == e2['UID']

def updated(new, old):
    ''' 
    The event has been updated if last-modified date has been changed.
    '''
    return old['LAST-MODIFIED'].dt != new['LAST-MODIFIED'].dt

def get_updates(new, old):
    ''' Get the differences between the new event and the old one
    
    Returns:
         update, dictionnary of updates made in the event
    '''
    update = {'UID': new['UID']}
    for k,v in new.items():
        if (not (k in NOT_UPDATED_KEYS)):
            print k, old[k]
            if (k in DATE_KEYS):
                if old[k].dt != v.dt:
                    update[k] = v
            elif old[k] != v:
                update[k] = v
    return update

def remove_duplicate(events):
    ''' Remove duplicate events.
    
    Some events are duplicated twice, i.e. same uid, summary and dates.
    However one of the duplicate has short description
    and most always no location attribute.
    Thus we keep the most described event when possible.

    Returns:
        events_cpy, list of events without duplicates.
    '''
    l = len(events)
    events_cpy = list(events)
    for i in range(l):
        for j in range(i+1, l):
            e1 = events[i]
            e2 = events[j]
            if event_equals(e1, e2):
                if e2["DESCRIPTION"] >= e1["DESCRIPTION"]:
                    events_cpy.remove(e1)
                else:
                    events_cpy.remove(e2)
    return events_cpy

def get_modifications(ade_cal):
    ''' Computes changes made on ade calendar
    Returns :
        modifs, dictionnary made of new and removed events and updates
    '''
    # Get old events with ICS_FILE
    if os.path.exists(ICS_FILE):
        ade_file = open(ICS_FILE, 'r')
        ade_file_content = ade_file.read()
        ade_file.close()
        try:
            ade_cal_old = Calendar.from_ical(ade_file_content)
        except Exception:
            ade_cal_old = Calendar()
    else:
        ade_cal_old = Calendar()
    
    events = remove_duplicate(ade_cal.walk('VEVENT'))
    old_events = remove_duplicate(ade_cal_old.walk('VEVENT'))

    #TODO : modify ade_cal in order to remove duplicates
    # i.e. build ade_cal from list events.
    f = open(ICS_FILE, 'w')
    f.write(ade_cal.to_ical())
    f.close()
    
    ev_cpy = list(events)
    old_cpy = list(old_events)

    updates = []

    # compute new and removed events and updates
    for e1 in ev_cpy:
        for e2 in old_cpy:
            if event_equals(e1, e2):
                if updated(e1, e2):
                    updates.append(get_updates(e1, e2))
                # if the events are equal then they are not new or removed
                events.remove(e1)
                old_events.remove(e2)
                    
    new_events = events
    removed_events = old_events

    modifs = {'new':new_events, 'removed':removed_events, 'updates': updates}
    return modifs

def ade_modif():
    # Get ade calendar from url if URL_FILE exists
    if os.path.exists(URL_FILE):
        url_file = open(URL_FILE, 'r')
        url = url_file.read()
        url_file.close()
        ade_cal = get_ade_cal(url)
    else:
        ade_cal = get_ade_cal()

    # Get modifications made on ade calendar   
    modif = get_modifications(ade_cal)
    
    return modif


def main():
    print ade_modif()

if __name__ == '__main__' :
    main()
