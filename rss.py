import feedparser
from datetime import datetime
from time import mktime
import logging
import config
from feeditem import Feeditem

rssfeeds = []

class RSSFeed:
    def __init__(self, name, url, max_count):
        self.name = name
        self.url = url
        self.max_count = max_count

    def parse(self):
        return feedparser.parse(self.url)

def get_feeds(feeds):
    feeditems = []

    for rssitem in feeds:
        count = 1
        for entry in rssitem.parse().entries:

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

            feeditems.append(
                Feeditem(
                    content,
                    'rss',
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
            if rssitem.max_count != -1 and count >= rssitem.max_count:
                break
            count += 1

    return feeditems

def reload_config():
    for rssitem in config.rss:
        rssfeeds.append(RSSFeed(rssitem['name'], rssitem['url'], rssitem['max_count']))

reload_config()
