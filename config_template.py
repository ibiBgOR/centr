import os
import keepass

with open('<file path to password for KeePass>') as f:
    content = f.readlines()

basedir = os.path.abspath(os.path.dirname(__file__)) # <dir path to the keepass file
databasefile = os.path.join(basedir, '<name of keepass file>')

extract = keepass.KeePassExtract(databasefile, content[0])

entry = extract.get_entry('runtastic')

runtastic = {
    'username': '<prename>-<surname>-<mail>',
    'user': '<username>', # or entry.username
    'password': '<password>', # or entry.password
}

rss = [
    {
        'name': '<name (showed on dashboard)>',
        'url': '<url>',
        'max_count': 5, # <maximal count of items>
    },
]

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
