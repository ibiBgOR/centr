import soundcloud
import datetime
import json
from config import soundcloud as config
from db import DBConnection, DBFeedItem

TYPE = 'soundcloud'

client = soundcloud.Client(
    client_id = config['client_id'],
    client_secret = config['client_secret'],
    username = config['username'],
    password = config['password']
)

conn = DBConnection()

accepted_types = [m for m in config['accepted_types'] if config['accepted_types'][m] == True]

def get_feeds():
    _load_feeds()

    feeds = conn.get_feeds(TYPE)

    #for feed in feeds:
    #    feed.content = json.load(feed.content)

    return feeds

def _load_feeds():
    # print client.get('/me/activities').next_href

    for element in client.get('/me/activities').collection:
        _type = element.type
        if _type not in accepted_types:
            continue

        if _type == 'track' or _type == 'track-repost':
            content = json.dumps({
                'username': element.origin.user['username'],
                'tracktitle': element.origin.title,
                'description': element.origin.description,
                'songurl': element.origin.permalink_url,
                'artworkurl': element.origin.artwork_url,
                'waveformurl': element.origin.waveform_url,
                'genre': element.origin.genre,
                'duration': element.origin.duration,
            })
        elif _type == 'comment':
            pass
        elif _type == 'favoriting':
            pass
        else:
            print 'Not accepted!'
            continue

        time = datetime.datetime.strptime(element.created_at, '%Y/%m/%d %H:%M:%S +%f') # e.g. 2016/02/17 15:03:31 +0000

        conn.insert_element(
            DBFeedItem(
                content,    # content
                TYPE,       # element type (soundcloud)
                _type,      # source (the type of the element from soundcloud)
                time        # time (as datetime)
            )
        )
