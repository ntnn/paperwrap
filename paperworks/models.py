from paperworks import wrapper
from fuzzywuzzy import fuzz
import logging
from threading import Thread

try:
    isinstance('string', basestring)
except NameError:
    basestring = str

logger = logging.getLogger(__name__)

use_threading = False


def threaded_method(func):
    def run(*args, **kwargs):
        if use_threading:
            Thread(target=func, args=args, kwargs=kwargs).start()
        else:
            func(*args, **kwargs)
    return run


class Model:
    def __init__(self, title, id, api):
        """Model for paperwork-objects.

        :type title: str
        :type id: integer
        :type api: wrapper.api
        """
        self.id = int(id)
        self.title = title
        self.api = api

    def __str__(self):
        return "{}:'{}'".format(self.id, self.title)

    def to_json(self):
        """Returns model as dict."""
        return {
            'id': self.id,
            'title': self.title
            }

    @classmethod
    def from_json(cls, json):
        """Creates model from json-dict.

        :param dict json: dictionary of json data
        """
        return cls(
            json['title'],
            json['id']
            )


class Notebook(Model):
    def __init__(self, title, id, api, type=0, updated_at=''):
        """Notebook paperwork-object.

        :type title: str
        :type id: integer
        :type api: wrapper.api
        :type updated_at: str
        """
        super().__init__(title, id, api)
        self.type = type
        self.updated_at = updated_at
        self.notes = {}

    def to_json(self):
        """Returns notebook as dict."""
        return {
            'type': self.type,
            'id': self.id,
            'title': self.title
            }

    @classmethod
    def from_json(cls, json, api):
        """Creates Notebook-instance from json-dict.

        :param dict json: dictionary of json data
        :param wrapper.api api: api-instance
        """
        return cls(
            json['title'],
            json['id'],
            api,
            type=json['type'],
            updated_at='')

    @classmethod
    def create(cls, api, title):
        """Sends a POST request to the host to create a notebook.

        :param wrapper.api api: api-instance
        :type title: str
        """
        logger.info('Created notebook {}'.format(title))
        return cls.from_json(api.create_notebook(title), api)

    @threaded_method
    def delete(self):
        """Deletes notebook from remote host."""
        logger.info('Deleting notebook {}'.format(self))
        self.api.delete_notebook(self.id)

    @threaded_method
    def update(self, force=True):
        """Updates local or remote notebook, depending on timestamp.

        :param bool force: If true the local title is pushed,
                           regardless of timestamp.
        """
        logger.info('Updating {}'.format(self))
        remote = self.api.get_notebook(self.id)
        if remote is None:
            logger.error('Remote notebook could not be found.'
                         'Wrong id or deleted.')
        elif force or remote['updated_at'] < self.updated_at:
            self.updated_at = self.api.update_notebook(
                self.to_json())['updated_at']
        else:
            logger.info('Remote version is higher.'
                        'Updating local notebook.')
            self.title = remote['title']
            self.updated_at = remote['updated_at']

    def get_notes(self):
        """Returns notes in an alphabetically sorted list.

        :rtype: list"""
        return sorted(self.notes.values(), key=lambda note: note.title)

    @threaded_method
    def create_note(self, title):
        """Creates a note.

        :type title: str
        """
        note = Note.create(title, self)
        self.notes[note.id] = note
        logger.info('Created note {} in {}'.format(note, self))

    @threaded_method
    def add_note(self, note):
        """Adds a note to the notebook.

        :type note: models.Note"""
        self.notes[note.id] = note
        logger.info('Added note {} to {}'.format(note, self))

    def download(self, tags):
        """Downloads notes.

        :param dict tags: Tags of the paperwork instance.
        """
        notes_json = self.api.list_notebook_notes(self.id)
        logger.info('Downloading notes of notebook {}'.format(self))
        for note_json in notes_json:
            note = Note.from_json(note_json, self)
            self.add_note(note)
            note.add_tags([tags[int(tag['id'])] for tag in note_json['tags']])


class Note(Model):
    def __init__(self, title, id, notebook, content='', updated_at=''):
        """Note paperwork-object.

        :type title: str
        :type id: int or str
        :type notebook: Notebook
        :type content: str
        :type updated_at: str
        """
        super().__init__(title, id, notebook.api)
        self.notebook = notebook
        self.content = content
        self.updated_at = updated_at
        self.tags = set()

    def to_json(self):
        """Returns note as dict."""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'tags': [tag.to_json() for tag in self.tags],
            'notebook_id': self.notebook.id
            }

    @classmethod
    def from_json(cls, json, notebook):
        """Creates note from dict.

        :type json: dict
        :type notebook: Notebook
        """
        return cls(
            json['title'],
            json['id'],
            notebook,
            json['content'],
            json['updated_at']
            )

    @classmethod
    def create(cls, title, notebook):
        """Creates note in notebook.

        :type title: str
        :type notebook: Notebook
        """
        logger.info('Creating note {} in notebook'.format(title, notebook))
        res = notebook.api.create_note(notebook.id, title)
        return cls(
            title,
            res['id'],
            notebook,
            '',
            res['updated_at']
            )

    @threaded_method
    def update(self, force=False):
        """Updates local or remote note, depending on timestamp.

        :param bool force: If true local values will be pushed regardless
                           of timestamp.
        """
        logger.info('Updating note {}'.format(self))
        remote = self.api.get_note(self.notebook.id, self.id)
        if remote is None:
            logger.error('Remote note could not be found. Wrong id,'
                         'deleted or moved to another notebook')
        elif force or remote['updated_at'] <= self.updated_at:
            logger.info('Remote version is lower or force update.'
                        'Updating remote note.')
            self.updated_at = self.api.update_note(
                self.to_json())['updated_at']
        else:
            logger.info('Remote version is higher. Updating local note.')
            self.title = remote['title']
            self.content = remote['content']
            self.updated_at = remote['updated_at']

    @threaded_method
    def delete(self):
        """Deletes note from remote host and notebook."""
        logger.info('Deleting note {} in notebook {}'.format(
            self, self.notebook))
        if self.id in self.notebook.notes:
            del(self.notebook.notes[self.id])
        self.api.delete_note(self.to_json())

    @threaded_method
    def add_tags(self, tags):
        """Adds a collection of tags to the note.

        :type tags: list or set"""
        for tag in tags:
            logger.info('Adding tag {} to note {}'.format(tag, self))
            self.tags.add(tag)

    @threaded_method
    def move_to(self, new_notebook):
        """Moves note to new_notebook.

        :type new_notebook: Notebook
        """
        self.api.move_note(self.to_json(), new_notebook.id)
        del(self.notebook.notes[self.id])
        new_notebook.add_note(self)


class Tag(Model):
    def __init__(self, title, id, api, visibility=0):
        """Tag paperwork-object.

        :type title: str
        :type id: int or str
        :type api: wrapper.api
        :type visibility: int
        """
        super().__init__(title, id, api)
        self.visibility = visibility
        self.notes = set()

    def to_json(self):
        """Returns tag as dict."""
        return {
            'id': self.id,
            'title': self.title,
            'visibility': self.visibility
            }

    @classmethod
    def from_json(cls, json, api):
        """Creates tag from dict.

        :type json: dict
        :type api: wrapper.api
        """
        return cls(
            json['title'],
            json['id'],
            api,
            json['visibility']
            )

    def get_notes(self):
        """Returns notes in a sorted list.

        :rtype: list"""
        return sorted(self.notes, key=lambda note: note.title)


class Paperwork:
    def __init__(self, user, passwd, host):
        """Paperwork object.

        :type user: str
        :type passwd: str
        :type host: str
        """
        self.notebooks = {}
        self.tags = {}
        self.api = wrapper.api()
        self.authenticated = self.api.basic_authentication(host, user, passwd)

    def create_notebook(self, title):
        """Creates notebook and adds it to paperwork.

        :type title: str
        :rtype: Notebook
        """
        if title != 'All Notes':
            notebook = Notebook.create(self.api, title)
            self.notebooks[notebook.id] = notebook
            logger.info('Created notebook {}'.format(notebook))
            return notebook

    @threaded_method
    def delete_notebook(self, nb):
        """Deletes notebook from server and instance.

        :type nb: Notebook
        """
        nb.delete()
        del(self.notebooks[nb.id])

    @threaded_method
    def add_notebook(self, notebook):
        """Adds notebook to paperwork.

        :type notebook: Notebook
        """
        if notebook.id != 0:
            self.notebooks[notebook.id] = notebook
            logger.info('Added notebook {}'.format(notebook))

    @threaded_method
    def add_tag(self, tag):
        """Adds tag to paperwork.

        :type tag: Tag
        """
        self.tags[tag.id] = tag
        logger.info('Added tag {}'.format(tag))

    def download(self):
        """Downloading tags, notebooks and notes from host."""
        logger.info('Downloading all')

        logger.info('Downloading tags')
        for tag in self.api.list_tags():
            tag = Tag.from_json(tag, self.api)
            self.tags[tag.id] = tag

        logger.info('Downloading notebooks')
        for notebook in self.api.list_notebooks():
            if notebook['title'] != 'All Notes':
                notebook = Notebook.from_json(notebook, self.api)
                self.add_notebook(notebook)
                notebook.download(self.tags)
            else:
                logger.info('Skipping notebook {}'.format(notebook))

    @threaded_method
    def update(self):
        """Updating notebooks and notes to host."""
        logger.info('Updating notebooks and notes')
        for nb in self.notebooks.values():
            nb.update()
            for note in nb.get_notes():
                note.update()

    def find(self, key, coll):
        """Finds key in given dict.

        :type key: str or int
        :type coll: dict
        :rtype: Notebook or Note or Tag or None
        """
        logger.info('Searching item for key {} of type {}'.format(
            key, type(key)))
        if isinstance(key, basestring):
            for item in coll.values():
                if key == item.title:
                    return item
            logger.error('No item found for key {} of type {}'.format(
                key, type(key)))
        else:
            return coll[key]

    def find_tag(self, key):
        """Finds tag with key (id or title).

        :type key: str or int
        :rtype: Tag or None
        """
        return self.find(key, self.tags)

    def find_notebook(self, key):
        """Find notebook with key (id or title).

        :type key: str or int
        :rtype: Notebook or None
        """
        return self.find(key, self.notebooks)

    def find_note(self, key):
        """Find note with key (id or title).

        :type key: str or int
        :rtype: Note or None
        """
        logger.info('Searching note for key {} of type {}'.format(
            key, type(key)))
        if isinstance(key, basestring):
            for item in self.get_notes():
                if key == item.title:
                    return item
        else:
            logger.info('key is int, finding through keys')
            for nb in self.notebooks.values():
                if key in nb.notes:
                    return nb.notes[key]
        logger.error('No note found for key {} of type {}'.format(
            key, type(key)))

    def fuzzy_find(self, title, choices):
        """Fuzzy find for title in choices. Returns highest match.

        :type title: str
        :type choices: list or set or tuple
        :rtype: Tag or Note or Notebook
        """
        top_choice = (0, None)
        for choice in choices:
            val = fuzz.ratio(choice.title, title)
            if val > top_choice[0]:
                top_choice = (val, choice)
        return top_choice[1]

    def fuzzy_find_tag(self, title):
        """Fuzzy search for tag with given title."""
        return self.fuzzy_find(title, self.tags.values())

    def fuzzy_find_notebook(self, title):
        """Fuzzy search for notebook with given title.

        :type title: str
        :rtype: Notebook
        """
        return self.fuzzy_find(title, self.notebooks.values())

    def fuzzy_find_note(self, title):
        """Fuzze search for note with given title.

        :type title: str
        :rtype: Note
        """
        return self.fuzzy_find(title, self.get_notes())

    def search(self, key):
        """Searches for given key and returns note-instances.

        :type key: str
        :rtype: List
        """
        json_notes = self.api.search(key)
        notes = []
        for json_note in json_notes:
            self.find_note(json_note['id'])
        return notes

    def get_notes(self):
        """Returns notes in a sorted list.

        :rtype: list
        """
        return sorted(
            [note for nb in self.notebooks.values()
             for note in nb.notes.values()],
            key=lambda note: note.title)

    def get_notebooks(self):
        """Returns notebooks in a sorted list.

        :rtype: list
        """
        return sorted(self.notebooks.values(), key=lambda nb: nb.title)

    def get_tags(self):
        """Returns tags in a sorted list.

        :rtype: list
        """
        return sorted(self.tags.values(), key=lambda tag: tag.title)
