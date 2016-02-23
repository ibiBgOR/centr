# Centr
There are millions of services out there. Each one comes with an extra dashboard. Centr aims to combine the dashboard of all services. Also Centr should be easily extensible for new services.

![Image of Centr](/centr.png?raw=true)

# Features
## Included Services:
- RSS Feed support
- Soundcloud (partly WIP)
- Reddit (partly WIP)

## Other Features:
- KeePass Connection

# Install and Run
1. `pip install -r requirements.txt`
2. `python main.py db upgrade`
3. `python main.py runserver`

**OR**

## For Linux:
1. `./install_and_run.sh`

## For Windows:
1. `install_and_run.bat`

# Contribute
You can contribute by adding issues and suggesting new services. Or you simply fork and make pull requests.

#TODO
[ ] Soundcloud (implement cards for comment)

[ ] Soundcloud (implement cards for favoriting)

[ ] Reddit (implement user login -> monitor new mails (new comments and new upvotes))

# License
This work is licensed under a [Creative Commons Attribution-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-sa/4.0/).

![License](https://i.creativecommons.org/l/by-sa/4.0/88x31.png)
