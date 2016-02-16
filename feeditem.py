from datetime import datetime

class Feeditem:
    def __init__(self, content, type_, source, time):
        self.content = content
        self.type = type_
        self.source = source
        self.time = time

    def get(self):
        return {
            'content': self.content,
            'type': self.type,
            'source': self.source,
            'time': str(self.time)
        }
