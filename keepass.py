import libkeepass

class KeePassExtract():
    def __init__(self, databasefile_, password_):
        self.databasefile = databasefile_
        self.password = password_

    def get_entry(self, title):
        if self.databasefile == None or self.password == None:
            print 'Not initalized'
            return None

        with libkeepass.open(self.databasefile, password = self.password) as kdb:
            found = False
            for entry in kdb.obj_root.findall('.//Entry'):
                for string in entry.findall('.//String'):
                    if string.find('.//Key') != 'Title':
                        continue
                    if string.find('.//Value') == title:
                        found = True
                        break

                if found:
                    for sting in entry.findall('.//String'):
                        if sting.find('.//Key') == 'Notes':
                            notes = sting.find('.//Value')
                        elif sting.find('.//Key') == 'Password':
                            password = sting.find('.//Value')
                        elif sting.find('.//Key') == 'Title':
                            title = sting.find('.//Value')
                        elif sting.find('.//Key') == 'URL':
                            url = sting.find('.//Value')
                        elif sting.find('.//Key') == 'UserName':
                            username = sting.find('.//Value')
                    return KeePassEntry(notes, password, title, url, username)

            return None

class KeePassEntry():
    def __init__(self, notes, password, title, url, username):
        self.notes = notes
        self.password = password
        self.title = title
        self.url = url
        self.username = username
