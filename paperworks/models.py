from paperworks import wrapper
from fuzzywuzzy import fuzz
import logging
import threading

logger = logging.getLogger('models')


class Model:
    def __init__(self, title, id, api):
        self.id = id
        self.title = title
        self.api = api

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
    def __init__(self, title, id, api, type=0, updated_at=''):
        super().__init__(title, id, api)
        self.type = type
        self.updated_at = updated_at
        self.notes = {}

    def to_json(self):
        return {
            'type': self.type,
            'id': self.id,
            'title': self.title
            }

    @classmethod
    def from_json(cls, json, api):
        return cls(
            json['title'],
            json['id'],
            api,
            type=json['type'],
            updated_at='')

    def add_note(self, note):
        """Adds note to notebook. Returns note instance."""
        logger.info('Adding note {} to notebook {}'.format(note, self))
        note.notebook = self
        note.pw = self.pw
        self.notes.add(note)
        return note

    def create_note(self, title, content=''):
        """Creates note with given title and adds it to the
        notebook. Returns note instance."""
        return self.add_note(Note(title, content=content))

    def remove_note(self, note):
        """Removes note from notebook. Does not delete note from server."""
        logger.info('Removing note {} to notebook {}'.format(note, self))
        self.notes.discard(note)

    def delete(self):
        """Deletes notebook from remote host."""
        if self.id == 0:
            logger.error('Error while removing notebook {}'.format(self))
        else:
            self.pw.api.delete_notebook(self.id)
        for note in self.get_notes():
            self.remove_note(note)
        self.pw.notebooks.discard(self)

    # TODO (Nelo Wallus): Default force to true when api
    # response is fixed
    def update(self, force=True):
        """Updates local or remote notebook, depending on timestamp.
        Creates if notebook id is 0."""
        if self.id == 0:
            self.id = self.pw.api.create_notebook(self.title)['id']
        else:
            remote = self.pw.api.get_notebook(self.id)
            if remote is None:
                logger.error('Remote notebook could not be found.'
                             'Wrong id or deleted.')
            elif force or remote['updated_at'] < self.updated_at:
                self.pw.api.update_notebook(self.to_json())
            else:
                logger.info('Remote version is higher.'
                            'Updating local notebook.')
                self.title = remote['title']
                self.updated_at = remote['updated_at']

    def get_notes(self):
        return sorted(self.notes, key=lambda note: note.title)


class Note(Model):
    def __init__(self, title, id, notebook, content='', updated_at=''):
        super().__init__(title, id, notebook.api)
        self.notebook = notebook
        self.content = content
        self.updated_at = updated_at
        self.tags = set()

    def to_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'tags': [tag.to_json() for tag in self.tags],
            'notebook_id': self.notebook.id
            }

    @classmethod
    def from_json(cls, json, notebook):
        return cls(
            json['title'],
            json['id'],
            notebook,
            json['content'],
            json['updated_at']
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
        if None in (notebook, self.notebook) or 0 in (
                notebook.id, self.notebook.id, self.id):
            logger.error('Error while moving note {} from {} to {}'.format(
                self, self.notebook, notebook))
        else:
            self.pw.api.move_note(self.to_json(), notebook.id)
        if self.notebook:
            self.notebook.remove_note(self)
        notebook.add_note(self)

    def delete(self):
        """Deletes note."""
        if self.id == 0:
            logger.error('Error while removing note {}'.format(self))
        else:
            self.pw.api.delete_note(self.to_json())
        if self.notebook:
            self.notebook.remove_note(self)

    def update(self, force=False):
        """Updates local or remote note, depending on timestamp.
        Creates if note id is 0."""
        if self.id == 0:
            resp = self.pw.api.create_note(self.notebook.id, self.title, self.content)
            self.id = resp['id']
            self.updated_at = resp['updated_at']
        else:
            remote = self.pw.api.get_note(self.notebook.id, self.id)
            if remote is None:
                logger.error('Remote note could not be found. Wrong id,'
                             'deleted or moved to another notebook')
            elif remote['updated_at'] <= self.updated_at or force:
                logger.info('Remote version is lower or force update.'
                            'Updating remote note.')
                self.updated_at = self.pw.api.update_note(self.to_json())['updated_at']
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

    def get_versions(self):
        versions = self.pw.api.list_versions(self)
        return [Version.from_json(version) for version in versions]


class Version(Model):
    def __init__(self, title, id, content, updated_at, previous_id):
        super().__init__(title, id=id)
        self.content = content
        self.updated_at = updated_at
        self.previous_id = previous_id

    @classmethod
    def from_json(cls, json):
        return cls(
            json['title'],
            json['id'],
            json['content'],
            json['updated_at'],
            json['previous_id']
            )


class Tag(Model):
    def __init__(self, title, id, api, visibility=0):
        super().__init__(title, id, api)
        self.visibility = visibility
        self.notes = set()

    def to_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'visibility': self.visibility
            }

    @classmethod
    def from_json(cls, json, api):
        return cls(
            json['title'],
            json['id'],
            api,
            json['visibility']
            )

    def get_notes(self):
        """Returns notes in a sorted list."""
        return sorted(self.notes, key=lambda note: note.title)


class Paperwork:
    def __init__(self, user, passwd, host='http://demo.paperwork.rocks/'):
        self.notebooks = set()
        self.tags = set()
        self.api = wrapper.api()
        self.authenticated = self.api.basic_authentication(host, user, passwd)

    def add_notebook(self, notebook):
        """Add a notebook to the paperwork instance. Returns
        notebook instance."""
        if not isinstance(notebook, Notebook):
            notebook = Notebook(notebook)
        if notebook.title != 'All Notes':
            logger.info('Added notebook {}'.format(notebook))
            notebook.pw = self
            self.notebooks.add(notebook)
            return notebook

    def add_tag(self, tag):
        """Add a tag to the paperwork instance. Return tag instance."""
        if not isinstance(tag, Tag):
            tag = Tag(tag)
        logger.info('Added tag {}'.format(tag))
        tag.pw = self
        self.tags.add(tag)
        return tag

    def get_notes(self):
        """Returns notes in a sorted list."""
        return sorted([note for nb in self.notebooks for note in nb.notes],
                      key=lambda note: note.title)

    def get_notebooks(self):
        """Returns notebooks in a sorted list."""
        return sorted(self.notebooks, key=lambda nb: nb.title)

    def get_tags(self):
        """Returns tags in a sorted list."""
        return sorted(self.tags, key=lambda tag: tag.title)

    def parse_json(self, json):
        """Parse given json into tag, note or notebook."""
        if 'visibility' in json.keys():
            return Tag.from_json(json)
        elif 'content' in json.keys():
            return Note.from_json(json)
        else:
            return Notebook.from_json(json)

    def download(self):
        """Downloading tags, notebooks and notes from host."""
        logger.info('Downloading all')

        logger.info('Downloading tags')
        for tag in self.api.list_tags():
            self.add_tag(self.parse_json(tag))

        logger.info('Downloading notebooks')
        for notebook in self.api.list_notebooks():
            self.add_notebook(self.parse_json(notebook))

        for nb in self.notebooks:
            if 'All Notes' in nb.title:
                logger.info('Not downloading notebook {}'.format(nb))
            logger.info('Downloading notes of notebook {}'.format(nb))
            notes_json = self.api.list_notebook_notes(nb.id)
            for note_json in notes_json:
                note = Note.from_json(note_json)
                note.add_tags(
                    [self.find_or_create_tag(tag['title'])
                        for tag in note_json['tags']]
                    )
                nb.add_note(note)

    def update(self):
        """Updating notebooks and notes to host."""
        logger.info('Updating notebooks and notes')
        for nb in self.notebooks:
            if 'All Notes' in nb.title:
                logger.info('Not updating notebook {}'.format(nb))
            nb.update()
            for note in nb.notes:
                note.update()

    def find_tag(self, key):
        """Finds tag with key (id or title)."""
        for tag in self.tags:
            if key in (tag.id, tag.title):
                return tag

    def find_or_create_tag(self, title):
        """Return tag if found, else return new tag instance."""
        return self.find_tag(title) or self.add_tag(Tag(title))

    def find_notebook(self, key):
        """Find notebook with key (id or title)."""
        for notebook in self.notebooks:
            if key in (notebook.id, notebook.title):
                return notebook

    def find_note(self, key):
        """Find note with key (id or title)."""
        for note in self.get_notes():
            if key in (note.id, note.title):
                return note

    def fuzzy_find(self, title, choices):
        """Fuzzy find for title in choices. Returns highest match."""
        top_choice = (0, None)
        for choice in choices:
            val = fuzz.ratio(choice.title, title)
            if val > top_choice[0]:
                top_choice = (val, choice)
        return top_choice[1]

    def fuzzy_find_tag(self, title):
        """Fuzzy search for tag with given title."""
        return self.fuzzy_find(title, self.get_tags())

    def fuzzy_find_notebook(self, title):
        """Fuzzy search for notebook with given title."""
        return self.fuzzy_find(title, self.get_notebooks())

    def fuzzy_find_note(self, title):
        """Fuzze search for note with given title."""
        return self.fuzzy_find(title, self.get_notes())

    def search(self, key):
        """Searches for given key and returns note-instances."""
        json_notes = self.api.search(key)
        notes = []
        for json_note in json_notes:
            self.find_note(json_note['id'])
        return notes
