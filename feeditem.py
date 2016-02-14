class Feeditem:
    def __init__(self, content, type, source, time):
        self.content = content
        self.type = type
        self.source = source
        self.time = time

    def get(self):
        return {
            'content': self.content,
            'type': self.type,
            'source': self.source,
            'time': self.time
        }
