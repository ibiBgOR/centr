from config import github as config
from github3 import GitHub
from requests.exceptions import ConnectionError
import logging

gh = GitHub(login = config['username'], password = config['password'])
events = gh.user(config['username']).iter_received_events(public = True)

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
    'WatchEvent': '{event.actor.login} {action} {event.repo[0]}/{event.repo[1]}',
}

for event in events:
    if event.type in type_header_map:
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
    else:
        print event

def get_feeds():
    pass

def _load_feeds():
    try:
        # print gh.events.list().all()
        pass
    except ConnectionError, e:
        print str(e)
