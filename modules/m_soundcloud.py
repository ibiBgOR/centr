import soundcloud
import datetime
import json
from requests.exceptions import ConnectionError
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
    result = []

    feeds = conn.get_feeds(TYPE)

    count = 0

    for feed in feeds:
        if count >= config['max_count']:
            break

        result.append(Feeditem(
            content = json.loads(feed.content),
            type = feed.type,
            source = feed.source,
            time = feed.time,
            link = feed.link,
        ))

        count += 1

    return result

def _load_feeds():
    # print client.get('/me/activities').next_href

    try:
        elements = client.get('/me/activities').collection
        for element in elements:
            _type = element.type
            if _type not in accepted_types:
                continue

            content = None
            link = None

            source = source_type_mapping[_type]

            if _type == 'track' or _type == 'track-repost':
                content = json.dumps({
                    'id': element.origin.id,
                    'username': element.origin.user['username'],
                    'tracktitle': element.origin.title,
                    'description': element.origin.description,
                    'songurl': element.origin.permalink_url,
                    'artworkurl': element.origin.artwork_url.replace('large', 't300x300'),
                    'waveformurl': element.origin.waveform_url,
                    'genre': element.origin.genre,
                    'duration': element.origin.duration,
                })
                source = source.format(element.origin.user['username'])
                link = element.origin.permalink_url
            elif _type == 'comment':
                pass
            elif _type == 'favoriting':
                pass
            else:
                print 'Not accepted!'
                continue

            time = datetime.datetime.strptime(element.created_at, '%Y/%m/%d %H:%M:%S +%f') # e.g. 2016/02/17 15:03:31 +0000
            _save_element(content, source, time, link)
    except ConnectionError, e:
        return
    except Exception, e:
        return

def _save_element(content, source, time, link):
    conn.insert_element(
        DBFeedItem(
            content,    # content
            TYPE,       # element type (soundcloud)
            source,     # source (the type of the element from soundcloud)
            time,       # time (as datetime)
            link,       # link to source
        )
    )
