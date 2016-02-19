import praw
from datetime import datetime
from time import mktime
from config import reddit as config
from db import DBConnection, DBFeedItem
from feeditem import Feeditem
from main import app

TYPE = 'reddit'

conn = DBConnection()
reddit_conn = praw.Reddit(user_agent = 'centr')

class RedditFeed:
    def __init__(self, name, url, max_count):
        self.name = name
        self.url = url
        self.max_count = max_count

def get_feeds():
    _load_feeds()

    result = []

    feeds = conn.get_feeds(TYPE)

    count = 0

    for feed in feeds:
        if count >= 2: #TODO: Max from config
            break

        result.append(Feeditem(
            content = feed.content,
            type = feed.type,
            source = feed.source,
            time = feed.time,
        ))

        count += 1

    return result

def _load_feeds():
    if 'subreddits' in config:
        for subreddit in config['subreddits']:
            for post in reddit_conn.get_subreddit(subreddit['name']).get_new():
                conn.insert_element(DBFeedItem(
                    post.title, # content
                    TYPE, # type
                    'New post in subreddit {0}'.format(subreddit['name']), # source
                    _get_date(post), # time
                ))

    if 'users' in config:
        for user in config['users']:
            pass
            # print reddit_conn.get_redditor(user).get_submitted('new', 'all').get_content()

def reload_config():
    pass

def _get_date(submission):
    time = submission.created
    return datetime.fromtimestamp(time)
