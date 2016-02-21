import praw
from datetime import datetime
from time import mktime
from config import reddit as config
from db import DBConnection, DBFeedItem
from feeditem import Feeditem
from main import app
import json
from requests.exceptions import ConnectionError

TYPE = 'reddit'
USERS = 'u'
SUBREDDIT = 'r'

reddit_feeds = []

conn = DBConnection()
reddit_conn = praw.Reddit(user_agent = 'centr')

class RedditFeed:
    def __init__(self, name, source, max_count):
        self.name = name
        self.source = source
        self.max_count = max_count

def get_feeds():
    _load_feeds()

    result = []

    feedsources = []
    feed_map = {}

    if reddit_feeds == []:
        return None

    count = 0
    for feed in reddit_feeds:
        if feed.source == USERS:
            src = 'User {0} commented on a post'.format(feed.name)
        elif feed.source == SUBREDDIT:
            src = 'New post in subreddit {0}'.format(feed.name)
        else:
            continue

        feedsources.append({'src': src, 'counter': 0, 'max_count': feed.max_count})
        feed_map[src] = count
        count += 1

    feeds = conn.get_feeds(TYPE)

    for feed in feeds:

        if feed.source in [elem['src'] for elem in feedsources]:
            max_count = feedsources[feed_map[feed.source]]['max_count']
        else:
            max_count = 0

        try:
            if max_count != -1 and feedsources[feed_map[feed.source]]['counter'] >= max_count:
                continue
        except KeyError, e:
            # if the feed source is no longer available in the config
            continue

        result.append(Feeditem(
            json.loads(feed.content),
            TYPE,
            feed.source,
            feed.time
        ))
        feedsources[feed_map[feed.source]]['counter'] += 1

    return result

def _load_feeds():
    for element in reddit_feeds:
        if element.source == SUBREDDIT:
            #try:
            posts = reddit_conn.get_subreddit(element.name).get_new()
            for post in posts:
                conn.insert_element(DBFeedItem(
                    json.dumps({'content': post.title}), # content
                    TYPE, # type
                    'New post in subreddit {0}'.format(element.name), # source
                    _get_date(post), # time
                ))
            #except ConnectionError, e:
            #    print str(e)

        elif element.source == USERS:
            #try:
            redditor = reddit_conn.get_redditor(element.name)
            for comment in redditor.get_overview(sort = 'new', time = 'all'):
                print dir(comment)

                content = {}

                if hasattr(comment, 'body_html'):
                    content['content'] = comment.body_html

                if hasattr(comment, 'selftext_html'):
                    content['post_name'] = comment.selftext_html
                elif hasattr(comment, 'link_title'):
                    content['post_name'] = comment.link_title
                else:
                    print dir(comment)
                    continue

                conn.insert_element(DBFeedItem(
                    json.dumps(content), # content
                    TYPE, # type
                    'User {0} commented on a post'.format(element.name), # source
                    _get_date(post), # time
                ))
            #except Exception, e:#ConnectionError, e:
            #    print str(e)

            # print reddit_conn.get_redditor(user).get_submitted('new', 'all').get_content()

def reload_config():
    if 'subreddits' in config:
        for reddititem in config['subreddits']:
            reddit_feeds.append(RedditFeed(reddititem['name'], SUBREDDIT, reddititem['max_count']))
    if 'users' in config:
        for useritem in config['users']:
            reddit_feeds.append(RedditFeed(useritem['name'], USERS, useritem['max_count']))


reload_config()

def _get_date(submission):
    time = submission.created_utc
    return datetime.fromtimestamp(time)
