#License: MIT
#Author: Nelo Wallus, http://github.com/ntnn

import logging

logger = logging.getLogger('models')

class Model:
    def __init__(self, title, id, paperwork = None):
        self.id = id
        self.title = title
        self.pw = paperwork

    def __str__(self):
        return "{}:'{}'".format(self.id, self.title)

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
    def __init__(self, title, id = 0, paperwork = None):
        super().__init__(title, id, paperwork)
        self.notes = set()

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
        """Adds note to notebook. Returns note instance."""
        logger.info('Adding note {} to notebook {}'.format(note, self))
        note.notebook = self
        note.pw = self.pw
        self.notes.add(note)
        return note


class Note(Model):
    def __init__(self, title, id = 0, content = '', tags = set(), paperwork = None, updated_at = ''):
        super().__init__(title, id, paperwork)
        self.content = content
        # TODO (Nelo Wallus): This is ugly.
        self.tags = set()
        self.add_tags(tags)
        self.updated_at = updated_at

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
                json['content'],
                updated_at = json['updated_at']
                )

    @classmethod
    def from_file(cls, f, pw):
        firstline = f.readline()
        if 'id:' in firstline:
            note_id = firstline.split(':')[1].strip('\n')
            note_tags = f.readline().split(':')[1].strip('\n').split()
            note_content = f.read()
            tags = set( [ pw.find_or_create_tag(tag) for tag in note_tags ]   )
        else:
            note_id = 0
            note_content = firstline + f.read()
            tags = set()
        return cls(
                f.name.rsplit('/', 1)[1],
                note_id,
                note_content,
                tags
                )

    def add_tag(self, tag):
        """Adds tag to note. Sets reference to note in tag."""
        logger.info('Adding tag {} to note {}'.format(tag, self))
        tag.notes.add(self)
        self.tags.add(tag)

    def add_tags(self, tags):
        """Adds multiple tags to note."""
        for tag in tags:
            self.add_tag(tag)

    def string_tags(self):
        """Returns tag names in a string, separated by spaces."""
        ret = ''
        for tag in self.tags:
            ret += tag.title + ' '
        return ret

    def move_to(self, notebook):
        """Moves note to given notebook instance."""
        if None in (notebook, self.notebook) or 0 in (notebook.id, self.notebook.id, self.id):
            logger.error('Error while moving note {} from {} to {}'.format(self, self.notebook, notebook))
        else:
            self.pw.api.move_note(self.to_json(), notebook.id)
        self.notebook.delete_note(self)
        notebook.add_note(self)

    def delete(self):
        """Deletes note."""
        if self.id == 0:
            logger.error('Error while removing note {}'.format(self))
        else:
            self.pw.api.delete_note(self.id)
        self.notebook.delete_note(self)

    def update(self, force = False):
        """Updates local or remote note, depending on timestamp. Creates if note id is 0."""
        if self.id == 0:
            self.id = self.pw.api.create_note(self.to_json())['id']
        else:
            remote = self.pw.api.get_note(self.notebook.id, self.id)
            if remote is None:
                logger.error('Remote note could not be found. Wrong id, deleted or moved to another notebook.')
            elif remote['updated_at'] < self.updated_at or force:
                logger.info('Remote version is lower. Updating remote note.')
                self.pw.api.update_note(self.to_json())
            else:
                logger.info('Remote version is higher. Updating local note.')
                self.title = remote['title']
                self.content = remote['content']
                self.updated_at = remote['updated_at']
                self.tags = set()
                # TODO (Nelo Wallus): Create tags with
                # correct id if not available
                for tag in remote['tags']:
                    self.add_tag(self.pw.find_or_create_tag(tag['title']))

class Tag(Model):
    def __init__(self, title, id = 0, visibility = 0, notes = set(), paperwork = None):
        super().__init__(title, id, paperwork)
        self.visibility = visibility
        self.notes = notes

    def to_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'visibility': self.visibility
            }

    @classmethod
    def from_json(cls, json):
        return cls(
                json['title'],
                json['id'],
                json['visibility']
                )
