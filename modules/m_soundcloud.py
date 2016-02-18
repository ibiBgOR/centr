import soundcloud
import datetime
import json
from config import soundcloud as config
from db import DBConnection, DBFeedItem
from feeditem import Feeditem

TYPE = 'soundcloud'

client = soundcloud.Client(
    client_id = config['client_id'],
    client_secret = config['client_secret'],
    username = config['username'],
    password = config['password']
)

conn = DBConnection()

accepted_types = [m for m in config['accepted_types'] if config['accepted_types'][m] == True]

source_type_mapping = {
    'track': u'A new song was uploaded by {0}',
    'track-repost': u'A song was reposted by {0}',
    'comment': u'A new comment was given',
    'favoriting': u'Someone liked a song'
}

def get_feeds():
    _load_feeds()

    result = []

    feeds = conn.get_feeds(TYPE)

    for feed in feeds:
        result.append(Feeditem(
            content = json.loads(feed.content),
            type = feed.type,
            source = feed.source,
            time = feed.time,
        ))

    return result

def _load_feeds():
    # print client.get('/me/activities').next_href

    try:
        elements = client.get('/me/activities').collection
    except Exception, e:
        return

    for element in elements:
        _type = element.type
        if _type not in accepted_types:
            continue

        source = source_type_mapping[_type]

        if _type == 'track' or _type == 'track-repost':
            content = json.dumps({
                'id': element.origin.id,
                'username': element.origin.user['username'],
                'tracktitle': element.origin.title,
                'description': element.origin.description,
                'songurl': element.origin.permalink_url,
                'artworkurl': element.origin.artwork_url,
                'waveformurl': element.origin.waveform_url,
                'genre': element.origin.genre,
                'duration': element.origin.duration,
            })
            source = source.format(element.origin.user['username'])
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
                source,      # source (the type of the element from soundcloud)
                time        # time (as datetime)
            )
        )
