import wrapper
import logging

logger = logging.getLogger('models')

class Model:
    def __init__(self, title, id):
        self.id = id
        self.title = title

    @classmethod
    def from_json(cls, json):
        """Returns a model filled with data from given json."""
        return cls(json['id'], json['title'])

    def to_json(self):
        return {
                'id': self.id,
                'title': self.title
                }

class Notebook(Model):
    def __init__(self, title, id = 0, notes = []):
        super().__init__(title, id)
        self.notes = notes

    @classmethod
    def from_json(cls, json):
        return cls(json['title'],
                json['id'],
                [ Note.from_json(child, cls) for child in wrapper.list_notebook_notes(json['id']) ])

    def to_json(self):
        return super().to_json()

    def upload():
        if self.id is 0:
            try:
                self.id = wrapper.create_notebook(self.title)['id']
            except Error as e:
                logger.error(e)
        for note in notes:
            note.upload()

class Note(Model):
    def __init__(self, title, id = 0, content = '', tags = [], notebook = None):
        super().__init__(title, id)
        self.content = content
        self.tags = tags
        self.notebook = notebook

    @classmethod
    def from_json(cls, json, notebook):
        return cls(json['title'],
                json['id'],
                json['content'],
                [ Model.from_json(tag) for tag in json['tags'] ],
                notebook)

    def to_json(self):
        ret = super().to_json()
        ret.update({
            'content': self.content,
            'tags': self.tags
            })
        return ret

    def upload():
        try:
            if self.id is 0:
                    self.id = wrapper.create_note(self.notebook.id, self.title, self.content)['id']
            else:
                wrapper.update_note(self.to_json)
        except Error as e:
            logger.error(e)
