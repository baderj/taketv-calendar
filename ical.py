from BeautifulSoup import BeautifulSoup
import requests
import re
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import pytz

def get_stream_events():
    events = []
    html = requests.get('http://www.taketv.net/streams').text    
    doc = BeautifulSoup(html)   
    entries = []    
    for h2 in doc.findAll('h2'):
        who = h2.getText().encode('utf-8')        
        date = h2.findPrevious('span', {'class':'datum'}).getText()
        time = h2.findPrevious('span', {'class':'time'}).getText()
        when_dt = datetime.strptime('{0} {1}'.format(date,time), '%d.%m %H:%Mh')
        when_dt = when_dt.replace(year=datetime.now().year)        
        berlin = pytz.timezone('Europe/Berlin')
        event = {
        'summary': 'TakeTV - {0}'.format(who),        
        'location': 'www.twitch.tv/taketv',        
        'created': datetime.utcnow().replace(tzinfo=pytz.utc),
        'start' : when_dt.replace(tzinfo=berlin),
        'end' : (when_dt+timedelta(hours=2,minutes=30)).replace(tzinfo=berlin),
        }
        events.append( event )
    return events
    
def create_calendar(events):
    cal = Calendar()
    cal.add('proid', 'TakeTV Streaming Dates')
    cal.add('version', '2.0')
    
    for e in events:
        event = Event()
        event.add('summary', e['summary'])        
        event.add('dtstart',e['start'])
        event.add('dtend',e['end'])
        event.add('dtstamp',e['created'])
        event.add('location', e['location'])
        event['uid'] = "{0}#{1}".format(e['start'],e['summary'])
        cal.add_component(event)
    return cal

def write_to_file(path, cal):
    with open(path, 'wb') as f:
        f.write(cal.to_ical())
        
if __name__ == "__main__":
    events = get_stream_events()
    cal = create_calendar(events)
    write_to_file('taketv.ics', cal)