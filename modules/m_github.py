from config import github as config
from pygithub3 import Github
from requests.exceptions import ConnectionError
import logging

gh = Github(login = config['username'], password = config['password'])

def get_feeds():
    pass

def _load_feeds():
    try:
        # print gh.events.list().all()
        pass
    except ConnectionError, e:
        print str(e)
