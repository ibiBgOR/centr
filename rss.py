import feedparser
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
            feeditems.append(Feeditem(entry.content[0].value, 'rss', rssitem.name, entry.updated))
            if count >= rssitem.max_count:
                break
            count += 1

    return feeditems

def reload_config():
    for rssitem in config.rss:
        rssfeeds.append(RSSFeed(rssitem['name'], rssitem['url'], rssitem['max_count']))

reload_config()
