#License: MIT
#Author: Nelo Wallus, http://github.com/ntnn

import logging

logger = logging.getLogger('models')

class Model:
    def __init__(self, title, id):
        self.id = id
        self.title = title

    def to_json(self):
        """Return model as json-dict."""
        return {
                'id': self.id,
                'title': self.title
                }

    @classmethod
    def from_json(cls, json):
        """Creates model from json-dict."""
        return cls(
                json['title'],
                json['id']
                )

class Notebook(Model):
    def __init__(self, title, id = 0, notes = set()):
        super().__init__(title, id)
        self.notes = notes

    def to_json(self):
        return {
            'type': 0,
            'id': self.id,
            'title': self.title
            }

    @classmethod
    def from_json(cls, json):
        return super().from_json(json)

    def add_note(self, note):
        """Adds note to notebook. Sets reference to notebook in note."""
        logger.info('Adding note {}:{} to notebook {}:{}'.format(note.id, note.title, self.id, self.title))
        note.notebook = self
        self.notes.add(note)


class Note(Model):
    def __init__(self, title, id = 0, content = '', tags = set(), notebook = None):
        super().__init__(title, id)
        self.content = content
        self.tags = tags
        self.notebook = notebook

    def to_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'tags': [ tag.to_json() for tag in self.tags ],
            'notebook_id': self.notebook.id
            }

    @classmethod
    def from_json(cls, json):
        return cls(
                json['title'],
                json['id'],
                json['content']
                )

    def add_tag(self, tag):
        """Adds tag to note. Sets reference to note in tag."""
        logger.info('Adding tag {}:{} to note {}:{}'.format(tag.id, tag.title, self.id, self.title))
        tag.notes.add(self)
        self.tags.add(tag)

class Tag(Model):
    def __init__(self, title, id = 0, visibility = 0, notes = set()):
        super().__init__(title, id)
        self.visibility = visibility
        self.notes = notes

    def to_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'visibility': self.visibility
            }
