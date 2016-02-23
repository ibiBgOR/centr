from config import github as config
from pygithub3 import Github
from requests.exceptions import ConnectionError

gh = Github(login = config['username'], password = config['password'])

def get_feeds():
    try:
        print gh.events.list().all()
    except ConnectionError, e:
        print str(e)
