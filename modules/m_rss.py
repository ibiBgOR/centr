import feedparser
from datetime import datetime
from time import mktime
import logging
import config
from db import DBConnection, DBFeedItem

rssfeeds = []

TYPE = 'rss'

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

    _load_feeds(rssfeeds)

    feedsources = []
    feed_map = {}

    # if no rss feeds in config return
    if rssfeeds == []:
        return None

    count = 0
    for feed in rssfeeds:
        feedsources.append({'src': feed.name, 'counter': 0, 'max_count': feed.max_count})
        feed_map[feed.name] = count
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

def _load_feeds(feeds):
    for rssfeed in feeds:
        for entry in rssfeed.parse().entries:
            # parse loaded data
            content = ''
            try:
                if entry.content[0].value == '':
                    continue
                content = entry.content[0].value
            except AttributeError, e:
                #logging.error(str(e) + ' element: ' + str(entry), exc_info = True)
                if entry.summary_detail.value == '':
                    continue
                content = entry.summary_detail.value

            date = entry.updated_parsed

            # insert into database
            conn.insert_element(
                DBFeedItem(
                    content,
                    TYPE,
                    rssfeed.name,
                    datetime(
                        date.tm_year,
                        date.tm_mon,
                        date.tm_mday,
                        date.tm_hour,
                        date.tm_min,
                        date.tm_sec
                    )
                )
            )

def reload_config():
    for rssitem in config.rss:
        rssfeeds.append(RSSFeed(rssitem['name'], rssitem['url'], rssitem['max_count']))

reload_config()