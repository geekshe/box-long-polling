# Import modules ###############################################################

import requests
import os

# Define global variables ######################################################

# Import developer token from the environment via secrets.sh to
# avoid checking tokens into Git
developer_token = os.environ['DEVELOPER_TOKEN']
events_url = 'https://api.box.com/2.0/events'
headers = {'Authorization': 'Bearer {}'.format(developer_token)}

# Define helper functions ######################################################


def get_first_position(position):
    """ Retrieve the next stream position from the Box Events endpoint.

        The first time it is called with the position 'now'. After an event is
        triggered, it is called with the stream position for the next event.
    """

    position = 'now'
    params = {'stream_position': position}

    r = requests.get(events_url, headers=headers, params=params)
    return r.json()['next_stream_position']


def get_next_position(position):
    """ Retrieve the next stream position from the Box Events endpoint.

        The first time it is called with the position 'now'. After an event is
        triggered, it is called with the stream position for the next event.
    """

    position = position
    params = {'stream_position': position}

    r = requests.get(events_url, headers=headers, params=params)
    return r.json()['next_stream_position']


def get_poll_url():
    """ Retrieve the unique polling URL for this Box user. """

    r = requests.options(events_url, headers=headers)
    return r.json()['entries'][0]['url']


def get_event(position):
    """ Given a stream position, retrieve details for the event at that
        position. """

    position = position
    params = {'stream_position': position}

    r = requests.get(events_url, headers=headers, params=params)

    return r.json()


def poll_events(position, poll_url):
    """ Given a stream posititon and polling URL, listen for new events and
        return their details. """

    # Retrieve arguments for use in function
    params = position
    poll_url = poll_url

    r = requests.get(poll_url, headers=headers, params=params)

    msg = r.json()['message']
    print 'Event: {}'.format(msg)

    if msg == 'new_change':
        print "Retrieving event details..."
        event = get_event(position)
        next_position = event['next_stream_position']

        # Print event_id and event_type to stdout
        print 'event_id: {} | event_type: {} | name: {}'.format(event['entries'][0]['event_id'], event['entries'][0]['event_type'], event['entries'][0]['source']['name'])

    return next_position


# Define core function #########################################################


def start_listener():
    """ Retrieve first stream position and polling URL, start event lister, and
        poll until stopped by keyboard interrupt """

    first_position = get_next_position('now')
    print first_position
    poll_url = get_poll_url()

    print 'Starting long polling...'
    print '(Type Ctrl + C to stop)'

    print 'Realtime URL: {}'.format(poll_url)
    print '\nWaiting for an event...\n'
    poll_events(first_position, poll_url)

    while True:
        print '\nWaiting for an event...\n'

        # Note: I was getting inconsistent results carrying the stream position
        # forward, so I opted to follow an event trigger with the nearest
        # 'now' event
        poll_events(get_next_position('now'), poll_url)

    return None

# Run function #################################################################

start_listener()
