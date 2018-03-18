import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

ID_FILE = "cal_id.txt"

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Replication project Agrall'

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'replication-project-agrall.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def get_service(credentials):
    """Gets calendar service from user credentials.

    Returns:
        service, the obtained service.
    """
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    return service

def get_cal_id(service):
    """Gets calendar id from storage.

    If no calendar id has been stored yet, create a new calendar and store its id.

    Returns:
        cal_id, the calendar id.
    """
    if os.path.exists(ID_FILE):
        file_id = open(ID_FILE, 'r')
        cal_id = file_id.read()
        file_id.close()
        calendars = service.calendarList().list().execute()['items']
        for cal in calendars:
            if cal['id'] == cal_id:
                return cal_id
    calendar = {"kind": "calendar#calendar",
                "description": "EDT obtenu a partir d'ADE",
                "summary": "EDT Universite"
    }
    google_cal = service.calendars().insert(body=calendar).execute()
    cal_id = google_cal['id']
    file_id = open(ID_FILE, 'w')
    file_id.write(cal_id)
    file_id.close()
    return cal_id

def adeId2GoogleId(ade_id):
    ''' Remove first three letters from ade_id
    '''
    return ade_id[3:]

def icalEvent2GoogleEvent(ical_event):
    ''' Builds an adequate body in order to add or update an event
    '''
    body = {}
    for k, v in ical_event.items():
        if k == "SUMMARY":
            body['summary'] = v
        elif k == "DTSTART":
            #body['start'] = ical_event.decode('DTSTART').isoformat()
            body['start'] = {'dateTime':v.dt.isoformat()}
        elif k == 'LOCATION':
            body['location'] = v
        elif k == 'DESCRIPTION':
            body['description'] = v
        elif k == 'UID':
            body['iCalUID'] = v
        elif k == 'DTEND':
            body['end'] = {'dateTime':v.dt.isoformat()}
    return body

def update_google_cal(id_cal, service, modifs):
    ''' Modify google calendar according to modifs 
    modifs has 3 entries : new, removed and updates
    new is a list of new events to be added to the google calendar
    removed is a list of events to be removed from the google calendar
    updates is a list of modifications to make on the google calendar.
    '''
    new_events = modifs['new']
    removed_events = modifs['removed']
    updated_events = modifs['updates']
    
    # Obtain list of current event from google_calendar
    events = service.events().list(calendarId=id_cal).execute()
    old_events = events.get('items', [])

    # Adding new events
    for e in new_events:
        body = icalEvent2GoogleEvent(e)
        try:
            print "adding event : " + body['summary']
            service.events().insert(calendarId=id_cal, body=body).execute()
            print "event added"
        except:
            print "event could not be added"
            # If the event already exists or has been previously deleted
            # on google calendar, then the insertion fails.
            print "event already exists or has been deleted ?"
            print
            pass

    # Removing events
    for rem in removed_events:
        for ev in old_events:
            if rem["UID"] == ev["iCalUID"]:
                try:
                    print "deleting event : " + ev['summary']
                    service.events().delete(calendarId=id_cal,
                                            eventId=ev["id"]).execute()
                    print "event deleted"
                except:
                    print "event could not be deleted"
                    print "maybe already deleted ?"
                    print
                    pass

    # Updating events
    for up in updated_events:
        for ev in old_events:
            if up['UID'] == ev['iCalUID']:
                try:
                    print "updating event : " + ev['summary']
                    # We only add values modified in ade
                    # if a value was modified in google calendar AND ade
                    # then modifications made on google calendar will be lost.
                    body = icalEvent2GoogleEvent(up)
                    # Complete body to match event
                    # Modifications made on values that are not updated
                    # are kept.
                    for k, v in body.items():
                        ev[k] = v
                    service.events().update(calendarId=id_cal,
                                            eventId=ev['id'],
                                            body=ev).execute()
                    print "event updated"
                except:
                    print "event could not be updated"
                    print "maybe you deleted it ?"
                    print
                    pass               
                
def main():
    credentials = get_credentials()
    service = get_service(credentials)
    cal_id = get_cal_id(service)

if __name__ == "__main__":
    main()    
