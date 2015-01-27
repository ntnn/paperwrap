from paperworks import wrapper
import logging

logger = logging.getLogger('models')


class Model:
    def __init__(self, title, id, paperwork=None, updated_at=''):
        self.id = id
        self.title = title
        self.pw = paperwork
        self.updated_at = updated_at

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
    def __init__(self, title, id=0, paperwork=None, updated_at=''):
        super().__init__(title, id, paperwork, updated_at)
        self.notes = set()

    def to_json(self):
        return {
            'type': 0,
            'id': self.id,
            'title': self.title
            }

    @classmethod
    def from_json(cls, json):
        return cls(
            json['title'],
            json['id']
            )

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

    def delete_note(self, note):
        """Deletes note from notebook."""
        logger.info('Removing note {} to notebook {}'.format(note, self))
        note.notebook = None
        self.notes.discard(note)

    def delete(self):
        """Deletes notebook from remote host."""
        if self.id == 0:
            logger.error('Error while removing notebook {}'.format(self))
        else:
            self.pw.api.delete_notebook(self.id)

    # TODO (Nelo Wallus): Default force to true when api
    # response is fixed
    def update(self, force=True):
        """Updates local or remote notebook, depending on
        timestamp. Creates if notebook id is 0."""
        if self.id == 0:
            self.id = self.pw.api.create_notebook(self.title)['id']
        else:
            remote = self.pw.api.get_notebook(self.id)
            if remote is None:
                logger.error(
                    'Remote notebook could not be found. Wrong id or deleted.')
            elif force or remote['updated_at'] < self.updated_at:
                self.pw.api.update_notebook(self.to_json())
            else:
                logger.info(
                    'Remote version is higher. Updating local notebook.')
                self.title = remote['title']
                self.updated_at = remote['updated_at']

    def get_notes(self):
        return list(self.notes).sort(key=lambda note: note.title)


class Note(Model):
    def __init__(
            self, title, id=0, content='', tags=set(),
            paperwork=None, updated_at=''):
        super().__init__(title, id, paperwork, updated_at)
        self.content = content
        # TODO (Nelo Wallus): This is ugly.
        self.tags = set()
        self.add_tags(tags)

    def to_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'tags': [tag.to_json() for tag in self.tags],
            'notebook_id': self.notebook.id
            }

    @classmethod
    def from_json(cls, json):
        return cls(
            json['title'],
            json['id'],
            json['content'],
            updated_at=json['updated_at']
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
        self.notebook.delete_note(self)
        notebook.add_note(self)

    def delete(self):
        """Deletes note."""
        if self.id == 0:
            logger.error('Error while removing note {}'.format(self))
        else:
            self.pw.api.delete_note(self.to_json())
        self.notebook.delete_note(self)

    def update(self, force=False):
        """Updates local or remote note, depending on
        timestamp. Creates if note id is 0."""
        if self.id == 0:
            self.id = self.pw.api.create_note(
                self.notebook.id, self.title, self.content)['id']
        else:
            remote = self.pw.api.get_note(self.notebook.id, self.id)
            if remote is None:
                logger.error('Remote note could not be found. Wrong id,'
                             'deleted or moved to another notebook')
            elif remote['updated_at'] <= self.updated_at or force:
                logger.info('Remote version is lower or force update.'
                            'Updating remote note.')
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
    def __init__(self, title, id=0, visibility=0, notes=set(), paperwork=None):
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

    def get_notes(self):
        return list(self.notes).sort(key=lambda note: note.title)


class Paperwork:
    def __init__(self, user, passwd, host='http://demo.paperwork.rocks/'):
        self.notebooks = set()
        self.tags = set()
        self.api = wrapper.api(user, passwd, host)

    def add_notebook(self, notebook):
        """Add a notebook to the paperwork instance. Returns
        notebook instance."""
        if isinstance(notebook, str):
            notebook = Notebook(notebook)
        logger.info('Added notebook {}'.format(notebook))
        notebook.pw = self
        self.notebooks.add(notebook)
        return notebook

    def add_tag(self, tag):
        """Add a tag to the paperwork instance. Return tag instance."""
        if isinstance(tag, str):
            tag = Tag(tag)
        logger.info('Added tag {}'.format(tag))
        tag.pw = self
        self.tags.add(tag)
        return tag

    def get_notes(self):
        return [note for notebook in self.notebooks for note in notebook.notes]

    def get_notebooks(self):
        return list(self.notebooks).sort(key=lambda nb: nb.title)

    def get_tags(self):
        return list(self.tags).sort(key=lambda tag: tag.title)

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
        for note in self.get_notes():
            if key in (note.id, note.title):
                return note

    def search(self, key):
        json_notes = self.api.search(key)
        notes = []
        for json_note in json_notes:
            self.find_note(json_note['id'])
        return notes
