import praw
from datetime import datetime
from time import mktime
from config import reddit as config
from db import DBConnection, DBFeedItem
from feeditem import Feeditem
from main import app
import logging
import json
from requests.exceptions import ConnectionError

TYPE = 'reddit'
USERS = 'u'
SUBREDDIT = 'r'

_logger = logging.getLogger(TYPE)

reddit_feeds = []

user_post_source_map = {
    'submission': 'User {0} has posted on subreddit {1}',
    'comment': 'User {0} commented on a post'
}
subreddit_action = 'New post in subreddit {0}'

conn = DBConnection()
reddit_conn = praw.Reddit(user_agent = 'centr')

class RedditFeed:
    def __init__(self, name, source, max_count):
        self.name = name
        self.source = source
        self.max_count = max_count

def get_feeds():
    result = []

    feedsources = []
    feed_map = {}

    if reddit_feeds == []:
        return None

    count = 0
    for feed in reddit_feeds:
        feedsources.append({'src': feed.name, 'counter': 0, 'max_count': feed.max_count})
        feed_map[feed.name] = count
        count += 1

    feeds = conn.get_feeds(TYPE)

    for feed in feeds:

        loaded_source = json.loads(feed.source)

        if loaded_source['title'] in [elem['src'] for elem in feedsources]:
            max_count = feedsources[feed_map[loaded_source['title']]]['max_count']
        else:
            max_count = 0

        try:
            if max_count != -1 and feedsources[feed_map[loaded_source['title']]]['counter'] >= max_count:
                continue
        except KeyError, e:
            # if the feed source is no longer available in the config
            continue

        if 'source' in loaded_source:
            # We get a user (is it a comment or a post?)
            if loaded_source['source'] == 'comment':
                source = user_post_source_map[loaded_source['source']].format(loaded_source['title'])
            elif loaded_source['source'] == 'submission':
                source = user_post_source_map[loaded_source['source']].format(loaded_source['title'], loaded_source['subreddit'])
        else:
            source = subreddit_action.format(loaded_source['title'])

        content = json.loads(feed.content)

        #if hasattr(content, 'content') and len(content['content']) > 0:
        #    content['content_first'] = ''
        #    content['content_additional'] = ''
        #
        #    counter = 0
        #    for item in content['content'].split('/n/n'):
        #        if counter >= 2:                            # only show 2 paragraphs
        #            content['content_additional'] += item
        #        else:
        #            content['content_first'] += item
        #        counter += 1

        result.append(Feeditem(
            content,
            TYPE,
            source,
            feed.time,
            feed.link
        ))
        feedsources[feed_map[loaded_source['title']]]['counter'] += 1

    return result

def _load_feeds():
    for element in reddit_feeds:
        if element.source == SUBREDDIT:
            try:
                posts = reddit_conn.get_subreddit(element.name).get_new()
                for post in posts:
                    content = {'post_name': post.title}

                    if hasattr(post, 'preview'):
                        img = {'source': '', 'width': 0}
                        preview = post.preview
                        for image in preview['images'][0]['resolutions']:
                            if image['width'] > 640:
                                continue
                            if image['width'] > img['width']:
                                img['source'] = image['url']
                                img['width'] = image['width']
                        content['thumbnail'] = img['source']

                    if hasattr(post, 'body'):
                        content['content'] = post.body
                    elif hasattr(post, 'selftext'):
                        content['content'] = post.selftext

                    url = ''

                    if hasattr(post, 'url'):
                        url = post.url
                    elif hasattr(post, 'permalink'):
                        url = post.permalink

                    conn.insert_element(DBFeedItem(
                        json.dumps(content), # content
                        TYPE, # type
                        json.dumps({'title': element.name}), # source
                        _get_date(post), # time
                        url, # link
                    ))
            except ConnectionError, e:
                _logger.error('There was an error with the connection. ' + str(e))

        elif element.source == USERS:
            try:
                redditor = reddit_conn.get_redditor(element.name)
                for comment in redditor.get_overview(sort = 'new', time = 'all'):
                    if isinstance(comment, praw.objects.Comment):
                        source = 'comment'
                    elif isinstance(comment, praw.objects.Submission):
                        source = 'submission'
                    else:
                        continue

                    content = {}

                    if hasattr(comment, 'body'):
                        content['content'] = comment.body
                    elif hasattr(comment, 'selftext'):
                        content['content'] = comment.selftext

                    subreddit = ''
                    if hasattr(comment, 'subreddit'):
                        subreddit = comment.subreddit.name

                    if hasattr(comment, 'title'):
                        content['post_name'] = comment.title
                    elif hasattr(comment, 'link_title'):
                        content['post_name'] = comment.link_title
                    else:
                        continue

                    url = ''

                    if hasattr(comment, 'url'):
                        url = comment.url
                    elif hasattr(comment, 'permalink'):
                        url = comment.permalink

                    conn.insert_element(DBFeedItem(
                        json.dumps(content), # content
                        TYPE, # type
                        json.dumps({'title': element.name, 'source': source, 'subreddit': subreddit}), # source
                        _get_date(comment), # time
                        url, # link
                    ))

            except ConnectionError, e:
                _logger.error('There was an error with the connection. ' + str(e))

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
