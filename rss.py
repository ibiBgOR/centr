import feedparser
from datetime import datetime
from time import mktime
import logging
import config
from feeditem import Feeditem
from db import DBConnection

rssfeeds = []

TYPE = 'rss'

class RSSFeed:
    def __init__(self, name, url, max_count):
        self.name = name
        self.url = url
        self.max_count = max_count

    def parse(self):
        return feedparser.parse(self.url)

def get_feeds(feeds):
    feeditems = []

    conn = DBConnection()

    _load_feeds(feeds)

    count = 0
    for item in conn.get_feeds(TYPE):
        feeditems.append(item)
        count += 1
        if rssitem.max_count != -1 and count >= rssitem.max_count:
            break

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
                logging.error(str(e) + ' element: ' + str(entry), exc_info = True)
                if entry.summary_detail.value == '':
                    continue
                content = entry.summary_detail.value

            date = entry.updated_parsed

            # insert into database
            conn = DBConnection()

            conn.insert_element(
                Feeditem(
                    content,
                    TYPE,
                    rssitem.name,
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
