import os
import keepass

with open('<file path to password for KeePass>') as f:
    content = f.readlines()

basedir = os.path.abspath(os.path.dirname(__file__)) # <dir path to the keepass file
databasefile = os.path.join(basedir, '<name of keepass file>')

extract = keepass.KeePassExtract(databasefile, content[0])

SHOW_LINKS = True   # indicates whether or not a link to the source side should be shown on the dashboard
DEBUG = False       # run the server in debug mode?

entry = extract.get_entry('github')

github = {
    'username': '<username>', # or entry.username,
    'password': '<password>', # or entry.password,
    'max_count': <max item count>,
    'accepted_types': {
        'CommitCommentEvent': True,
        'CreateEvent': True,
        'DeleteEvent': True,
        'ForkEvent': True,
        'GollumEvent': True,
        'IssueCommentEvent': True,
        'IssuesEvent': True,
        'MemberEvent': True,
        'PublicEvent': True,
        'PullRequestEvent': True,
        'PullRequestReviewCommentEvent': True,
        'PushEvent': True,
        'ReleaseEvent': True,
        'WatchEvent': True,
    }
}

reddit = {
    'subreddits': [
        {'name': '<subredditname>', 'max_count': <max item count>},
    ],
    'users': [
        {'name': '<username>', 'max_count': <max item count>},
    ],
}

rss = [
    {
        'name': '<name (showed on dashboard)>',
        'url': '<url>',
        'max_count': 5, # <maximal count of items>
    },
]

entry = extract.get_entry('runtastic')

runtastic = {
    'username': '<prename>-<surname>-<mail>',
    'user': '<username>', # or entry.username
    'password': '<password>', # or entry.password
}

entry = extract.get_entry('soundcloud')

soundcloud = {
    'client_id': '<client_id>',
    'client_secret': '<client_secret>',
    'username': '<username>', # or entry.username
    'password': '<password>', # or entry.password
    'max_count': 5, # <maximal count of items>,
    'accepted_types': {
        'track': True,
        'track-repost': True,
        'comment': True,
        'favoriting': True
    },
}
