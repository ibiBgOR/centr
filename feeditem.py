from datetime import datetime

class Feeditem:
    def __init__(self, content, type, source, time, link = ""):
        self.content = content
        self.type = type
        self.source = source
        self.time = time
        self.link = link

    def get(self):
        return {
            'content': self.content,
            'type': self.type,
            'source': self.source,
            'time': str(self.time),
            'link': self.link
        }
