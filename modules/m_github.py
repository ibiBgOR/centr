from config import github as config
from db import DBFeedItem, DBConnection
from github3 import GitHub
from requests.exceptions import ConnectionError
import logging
import datetime

gh = GitHub(config['username'], config['password'])
events = gh.user(config['username']).iter_received_events(public = True)

TYPE = 'github'

_logger = logging.getLogger(TYPE)
conn = DBConnection()

accepted_types = [m for m in config['accepted_types'] if config['accepted_types'][m] == True]
type_header_map = {
    'CommitCommentEvent': '{event.actor.login} commented on commit {event.repo[0]}/{event.repo[1]}@{rev_10}',
    'CreateEvent': '{event.actor.login} created {ref_type} {var_created}',
#    'DeleteEvent': 'A {ref_type} was deleted.', # TODO: format like github does
    'ForkEvent': '{event.actor.login} forked {event.repo[0]}/{event.repo[1]} to {forkee.full_name}',
    'GollumEvent': '{event.actor.login} edited the {event.repo[0]}/{event.repo[1]} wiki',
    'IssueCommentEvent': '{event.actor.login} commented on issue {event.repo[0]}/{event.repo[1]}#{issue.number}',
    'IssuesEvent': '{event.actor.login} {action} issue {event.repo[0]}/{event.repo[1]}#{issue.number}',
    'MemberEvent': '{event.actor.login} {action} {added_user.login} to {event.repo[0]}/{event.repo[1]}',
    'PublicEvent': '{event.actor.login} made {event.repo[0]}/{event.repo[1]} public',
    'PullRequestEvent': '{event.actor.login} {action} pull request {event.repo[0]}/{event.repo[1]}#{number}',
    'PullRequestReviewCommentEvent': '{event.actor.login} commented on pull request {event.repo[0]}/{event.repo[1]}#{number}',
    'PushEvent': '{event.actor.login} pushed to {ref} at {event.repo[0]}/{event.repo[1]}',
#    'ReleaseEvent': 'A new comment was given on a commit.', # TODO: format like github does
    'WatchEvent': '{event.actor.login} starred {event.repo[0]}/{event.repo[1]}',
}

def __get_link(event):
    return event.payload['comment'].html_url if 'comment' in event.payload and hasattr(event.payload['comment'], 'html_url') and event.payload['comment'].html_url != '' \
        else event.payload['issue'].html_url if 'issue' in event.payload and hasattr(event.payload['issue'], 'html_url') and event.payload['issue'].html_url != '' \
        else event.payload['release'].html_url if 'release' in event.payload and hasattr(event.payload['release'], 'html_url') and event.payload['release'].html_url != '' \
        else event.payload['pull_request'].html_url if 'pull_request' in event.payload and hasattr(event.payload['pull_request'], 'html_url') and event.payload['pull_request'].html_url != '' \
        else event.payload['html_url'] + '/wiki' if 'html_url' in event.payload and event.type == 'GollumEvent' \
        else event.payload['html_url'] + '/commits' if 'html_url' in event.payload and event.type == 'PushEvent' \
        else event.payload['forkee'].html_url if 'forkee' in event.payload and hasattr(event.payload['forkee'], 'html_url') and event.payload['forkee'].html_url != '' \
        else event.payload['html_url'] if 'html_url' in event.payload else None      # more or less a fallback. as far as i saw every payload got this field.

def get_feeds():
    result = []
    count = 0
    for feed in conn.get_feeds(TYPE):
        if count >= config['max_count']:
            break
        result.append(feed)
        count += 1
    return result

def _load_feeds():
    _logger.debug('Started to load feeds')
    try:
        for event in events:
            if event.type not in type_header_map:
                _logger.info('Unrecognised event: ' + str(event))
                continue

            if event.type not in accepted_types:
                continue

            payload = None
            if 'ref' in event.payload and event.payload['ref'] != None:
                payload = event.payload['ref']

            source = type_header_map[event.type].format(
                event = event,
                action = event.payload['action'] if 'action' in event.payload else '',
                issue = event.payload['issue'] if 'issue' in event.payload else '',
                ref_type = event.payload['ref_type'] if 'ref_type' in event.payload else '',
                var_created = (str(event.payload['ref']) + ' at ' + event.repo[0] + '/' + event.repo[1]) if ('ref' in event.payload and event.payload['ref'] != None)
                    else (event.repo[0] + '/' + event.repo[1]),
                forkee = event.payload['forkee'] if 'forkee' in event.payload else '',
                ref = payload[payload.rfind('/') + 1:] if (payload != None) else '',
                number = event.payload['number'] if 'number' in event.payload else '',
                rev_10 = event.payload['comment'].commit_id[:10] if ('comment' in event.payload and hasattr(event.payload['comment'], 'commit_id')) else '',
                added_user = event.payload['member'] if 'member' in event.payload else '',
            )

            date = event.created_at
            link = __get_link(event)
            if isinstance(link, dict) and 'href' in link:
                link = link['href'] # sometimes we get a dict from github.. so we catch this and just take the link from the dict

            _logger.debug('Insert new element to database.')
            conn.insert_element(
                DBFeedItem(
                    '',         # content
                    TYPE,       # element type (soundcloud)
                    source,     # source (the type of the element from soundcloud)
                    date,       # time (as datetime)
                    link,       # link to source
                )
            )
    except ConnectionError, e:
        _logger.error(str(e))
