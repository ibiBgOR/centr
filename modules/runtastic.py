# https://github.com/luser/runtastic-scrape

import html5lib
import json
import os
import re
import sys
import requests
import urlparse

known_sessions_file = os.path.join(os.path.dirname(__file__), 'known_sessions')

def get_user_id(doc):
    script = [s for s in doc.getElementsByTagName('script') if not s.hasAttribute('src') and 'var user =' in s.firstChild.wholeText]
    if not script:
        raise 'Can\'t find user id script'
    m = re.search('\{.*\}', script[0].firstChild.wholeText)
    if not m:
        raise 'Can\'t find user id data'
    return int(json.loads(m.group(0))['id'])

def get_data(doc):
    script = [s for s in doc.getElementsByTagName('script') if not s.hasAttribute('src') and 'var index_data =' in s.firstChild.wholeText]
    if not script:
        raise 'Can\'t find index_data script'
    m = re.search('\[.*\]', script[0].firstChild.wholeText)
    if not m:
        raise 'Can\'t find index_data data'
    return json.loads(m.group(0))

def get_csrf_token(doc):
    metas = doc.getElementsByTagName('meta')
    p = [m.getAttribute('content') for m in metas if m.getAttribute('name') == 'csrf-param']
    if not p:
        print 'No csrf-param'
    token_name = None
    if p:
        token_name = p[0]
    v = [m.getAttribute('content') for m in metas if m.getAttribute('name') == 'csrf-token']
    if not v:
        raise 'No csrf-token'
    token_value = v[0]
    return dict([(token_name, token_value)])

def read_known_sessions():
    if not os.path.isfile(known_sessions_file):
        return set()
    with open(known_sessions_file, 'rb') as f:
        return set(int(s.strip()) for s in f.readlines())

def write_known_sessions(data):
    with open(known_sessions_file, 'wb') as f:
        f.write('\n'.join(str(s) for s in sorted(data)))

def check_download_session(url, download_dir, cookies):
    r = requests.head(url, cookies=cookies)
    if r.status_code != 200 or 'Content-Disposition' not in r.headers:
        return False
    m = re.search('filename="(.+)"', r.headers['Content-Disposition'])
    if not m:
        return False
    f = m.group(1)
    filename = os.path.join(download_dir, f)
    if os.path.isfile(filename):
        return True
    # get it
    print "Fetching %s" % f
    r2 = requests.get(url, cookies=cookies)
    if r2.status_code != 200:
        return False
    with open(filename, 'wb') as f:
        f.write(r2.content)
    return True

def fetch_data(user, pw, download_dir=None):
    # Fetch the index page to get a CSRF token.
    r = requests.get('https://www.runtastic.com/')
    if r.status_code != 200:
        raise 'Sucks'
    cookies = dict(r.cookies)
    doc = html5lib.parse(r.text, treebuilder='dom')
    csrf = get_csrf_token(doc)
    # Now log in.
    # user, pw = read_user_pass()
    login = dict(csrf)
    login['user[email]'] = user
    login['user[password]'] = pw
    login['grant_type'] = 'password'
    r2 = requests.post('https://www.runtastic.com/de/d/benutzer/sign_in', data=login)#, cookies=cookies)
    if r2.status_code != 200:
        raise 'Sucks 2'
    cookies.update(r2.cookies)
    print r2.content
    j = r2.json()
    if not j['success']:
        raise 'Login failed'
    doc = html5lib.parse(j['update'], treebuilder='dom')
    # Find the sport-sessions page and fetch it to get a User ID
    # and a list of session IDs.
    links = [l.getAttribute('href') for l in doc.getElementsByTagName('a') if l.getAttribute('href').endswith('/sport-sessions')]
    sessions_url = urlparse.urljoin(r2.url, links[0])
    r3 = requests.get(sessions_url, cookies=cookies)
    if r3.status_code != 200:
        raise 'Sucks 3'
    cookies.update(r3.cookies)
    doc = html5lib.parse(r3.text, treebuilder='dom')
    uid = get_user_id(doc)
    data = get_data(doc)
    # Now hit the API to get data about each session.
    request_data = dict(csrf)
    request_data['user_id'] = uid
    request_data['items'] = ','.join(str(d[0]) for d in data)
    r4 = requests.post('https://www.runtastic.com/api/run_sessions/json',
                       cookies=cookies,
                       data=request_data)
    if r4.status_code != 200:
        raise 'Sucks 4'
    cookies.update(r4.cookies)
    sessions = r4.json()
    print sessions
    # known_sessions = read_known_sessions()
    # for s in sessions:
    #    if s['id'] in known_sessions:
    #        continue
    #    if check_download_session(urlparse.urljoin(r4.url, s['page_url']) + '.tcx', download_dir, cookies):
    #        known_sessions.add(s['id'])
    # write_known_sessions(known_sessions)

def read_user_pass():
    auth_file = os.path.join(os.path.dirname(__file__), 'auth')
    return [x.strip() for x in open(auth_file).read().splitlines()]
