#License: MIT
#Author: Nelo Wallus, http://github.com/ntnn

import wrapper
from models import *
import logging

logger = logging.getLogger('paperwork')

class Paperwork:
    def __init__(self, user, passwd, host = 'http://demo.paperwork.rocks/'):
        self.notebooks = set()
        self.tags = set()
        self.api = wrapper.api(user, passwd, host)

    def add_notebook(self, notebook):
        """Add a notebook to the paperwork instance."""
        if isinstance(notebook, str):
            notebook = Notebook(notebook)
        logger.info('Added notebook {}:{}'.format(notebook.id, notebook.title))
        self.notebooks.add(notebook)

    def add_tag(self, tag):
        """Add a tag to the paperwork instance."""
        if isinstance(tag, str):
            tag = Tag(tag)
        logger.info('Added tag {}:{}'.format(tag.id, tag.title))
        self.tags.add(tag)

    def parse_json(self, json):
        """Parse given json into tag, note or notebook."""
        if 'visibility' in json.keys():
            return self.parse_json_tag(json)
        elif 'content' in json.keys():
            return self.parse_json_note(json)
        else:
            return self.parse_json_notebook(json)

    def parse_json_tag(self, json):
        """Parses tag from given json. If tag exists it returns the Tag-instance."""
        logger.info('Parsing tag {}:{}'.format(json['id'], json['title']))
        return self.find_tag(json['id']) or Tag(json['title'], json['id'], json['visibility'])

    def parse_json_note(self, json):
        """Parses note from given json. Adds references to tags and notebooks."""
        #Iterates over the list of tag-dicts and adds from the paperwork.tags dict
        #Probably problematic
        logger.info('Parsing note {}:{}'.format(json['id'], json['title']))
        tags = set( [ self.parse_json_tag(tag) for tag in json['tags'] ] )
        return Note(
                json['title'],
                json['id'],
                json['content'],
                tags,
                self.find_notebook(json['notebook_id'])
                )

    def parse_json_notebook(self, json):
        """Parses notebook from given json. If notebook exists it returns the Notebook-instance."""
        logger.info('Parsing notebook {}:{}'.format(json['id'], json['title']))
        return self.find_notebook(json['id']) or Notebook(json['title'], json['id'])

    def download(self):
        """Downloading tags, notebooks and notes from host."""
        logger.info('Downloading all.')
        for tag in self.api.list_tags():
            self.add_tag(tag)
        for notebook in self.api.list_notebooks():
            self.add_notebook(notebook)
        for nb in self.notebooks:
            logger.info('Filling notebook {}:{}'.format(nb.id, nb.title))
            notes_json = self.api.list_notebook_notes(nb.id)
            for note_json in notes_json:
                note = Note.from_json(note_json)
                for tag in note_json['tags']:
                    note.add_tag(self.find_tag(tag['title']))
                nb.add_note(note)

    def upload(self):
        """Uploading notebooks and notes to host."""
        logger.info('Uploading all.')
        for nb in self.notebooks:
            self.api.update_notebook(nb.to_json())
            for note in nb.notes:
                self.api.update_note(note.to_json())

    def find_tag(self, key):
        """Finds tag with key."""
        for tag in self.tags:
            if key in (tag.id, tag.title):
                return tag

    def find_notebook(self, key):
        """Find notebook by id."""
        for notebook in self.notebooks:
            if key in (notebook.id, notebook.title):
                return notebook

if __name__ == '__main__':
    import unittest
    testsuite = unittest.TestLoader().discover('./tests/')
    unittest.TextTestRunner(verbosity=1).run(testsuite)
