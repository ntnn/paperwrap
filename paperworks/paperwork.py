#License: MIT
#Author: Nelo Wallus, http://github.com/ntnn

from paperworks import wrapper
from paperworks.models import *
import logging
import os
import json

logger = logging.getLogger('paperwork')

class Paperwork:
    def __init__(self, user, passwd, host = 'http://demo.paperwork.rocks/'):
        self.notebooks = set()
        self.tags = set()
        self.api = wrapper.api(user, passwd, host)

    def add_notebook(self, notebook):
        """Add a notebook to the paperwork instance. Returns notebook instance."""
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
            logger.info('Downloading notes of notebook {}'.format(nb))
            notes_json = self.api.list_notebook_notes(nb.id)
            for note_json in notes_json:
                note = Note.from_json(note_json)
                note.add_tags( [ self.find_or_create_tag(tag['title']) for tag in note_json['tags'] ] )
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

    def write_paperwork_to_disk(self, folder = 'paperwork'):
        """Downloads notebooks and notes to disk."""
        logger.info('Writing notebooks and notes to disk')
        if not os.path.exists(folder):
            os.makedirs(folder)

        logger.info('Writing tags file')
        with open(os.path.join(folder, '.tags'), 'w') as f:
            f.write(json.dumps([ tag.to_json() for tag in self.tags ]))

        logger.info('Writing notebooks')
        for nb in self.notebooks:

            # Do note write 'All Notes' notebook
            # TODO (Nelo Wallus): nb.id should be used
            if 'All Notes' in nb.title:
                logger.info('Not writing notebook {}'.format(nb))
                continue

            logger.info('Writing notebook {}'.format(nb))
            path = os.path.join(folder, nb.title)
            if not os.path.exists(path):
                os.makedirs(path)

            logger.info('Writing id file')
            with open(os.path.join(path, '.id'), 'w') as f:
                f.write(str(nb.id))

            for note in nb.notes:
                logger.info('Writing note {}'.format(note))
                with open(os.path.join(path, note.title), 'w') as f:
                    f.write('id:{}\ntags:{}\n{}'.format(note.id, note.string_tags(), note.content))

    def read_paperwork_from_disk(self, folder = 'paperwork'):
        """Read tags, notebooksand notes from disk."""
        logger.info('Reading paperwork from disk')

        logger.info('Reading notebook folders')
        nb_folders = os.listdir(folder)

        if '.tags' in nb_folders:
            logger.info('Reading tags file')
            with open(os.path.join(folder, '.tags'), 'r') as f:
                for tag in json.loads(f.read()):
                    self.add_tag(self.parse_json_tag(tag))
            nb_folders.remove('.tags')

        for nb_folder in nb_folders:
            logger.info('Reading notebook folder {}'.format(nb_folder))
            path = os.path.join(folder, nb_folder)
            nb_files = os.listdir(path)

            if '.id' in nb_files:
                logger.info('Reading id file')
                with open(path + '/.id', 'r') as f:
                    nb_id = f.read()
                nb_files.remove('.id')
            else:
                nb_id = 0
            nb = self.add_notebook(Notebook(nb_folder, nb_id))

            logger.info('Reading notes')
            for note_file in nb_files:
                logger.info('Reading note {}'.format(note_file))
                with open(os.path.join(folder, nb_folder, note_file), 'r') as f:
                    nb.add_note(Note.from_file(f, self))

    def find_tag(self, key):
        """Finds tag with key (id or title)."""
        for tag in self.tags:
            if key in (tag.id, tag.title):
                return tag

    def find_or_create_tag(self, title):
        """Return tag if found, else return new tag instance."""
        return self.find_tag(title) or self.add_tag(Tag(title))

    def find_notebook(self, key):
        """Find notebook by id."""
        for notebook in self.notebooks:
            if key in (notebook.id, notebook.title):
                return notebook
