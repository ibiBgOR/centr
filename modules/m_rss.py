import feedparser
import datetime
import logging
import config
from db import DBConnection, DBFeedItem

rssfeeds = []

TYPE = 'rss'
DATE_FORMATS = ['%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%M:%S+00:00']

conn = DBConnection()

class RSSFeed:
    def __init__(self, name, url, max_count):
        self.name = name
        self.url = url
        self.max_count = max_count

    def parse(self):
        return feedparser.parse(self.url)

def get_feeds():
    feeditems = []

    feedsources = []
    feed_map = {}

    # if no rss feeds in config return
    if rssfeeds == []:
        return None

    count = 0
    for feed in rssfeeds:
        feedsources.append({'src': 'A new post from ' + str(feed.name), 'counter': 0, 'max_count': feed.max_count})
        feed_map['A new post from ' + str(feed.name)] = count
        count += 1

    # Iterate over all rss feed items and decide wether or not to add them to the mainline
    for item in conn.get_feeds(TYPE):

        if item.source in [elem['src'] for elem in feedsources]:
            max_count = feedsources[feed_map[item.source]]['max_count']
        else:
            max_count = 0

        try:
            if max_count != -1 and feedsources[feed_map[item.source]]['counter'] >= max_count:
                continue
        except KeyError, e:
            # if the feed source is no longer available in the config
            continue

        feeditems.append(item)
        feedsources[feed_map[item.source]]['counter'] += 1

    return feeditems

def _load_feeds():
    reload_config()

    for rssfeed in rssfeeds:
        for entry in rssfeed.parse().entries:
            # parse loaded data
            content = ''

            if hasattr(entry, 'content') and hasattr(entry.content[0], 'value'):
                content = entry.content[0].value
            elif hasattr(entry, 'summary'):
                content = entry.summary
            elif hasattr(entry, 'description'):
                content = entry.description
            elif hasattr(entry, 'title'):
                content = entry.title

            if content == '':
                continue

            date = None

            if hasattr(entry, 'updated_parsed'):
                _date = entry.updated_parsed
                date = datetime.datetime(
                    _date.tm_year,
                    _date.tm_mon,
                    _date.tm_mday,
                    _date.tm_hour,
                    _date.tm_min,
                    _date.tm_sec
                )

            if date == None:
                continue

            # insert into database
            conn.insert_element(
                DBFeedItem(
                    content,
                    TYPE,
                    'A new post from ' + str(rssfeed.name),
                    date
                )
            )

def reload_config():
    for rssitem in config.rss:
        rssfeeds.append(RSSFeed(rssitem['name'], rssitem['url'], rssitem['max_count']))

reload_config()
