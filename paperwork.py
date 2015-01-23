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
        """Add a notebook to the paperwork instance. Returns notebook instance."""
        if isinstance(notebook, str):
            notebook = Notebook(notebook)
        logger.info('Added notebook {}'.format(notebook))
        self.notebooks.add(notebook)
        return notebook

    def add_tag(self, tag):
        """Add a tag to the paperwork instance. Return tag instance."""
        if isinstance(tag, str):
            tag = Tag(tag)
        logger.info('Added tag {}'.format(tag))
        self.tags.add(tag)
        return tag

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
        logger.info('Parsing json tag {}:{}'.format(json['id'], json['title']))
        return self.find_tag(json['id']) or Tag(json['title'], json['id'], json['visibility'])

    def parse_json_note(self, json):
        """Parses note from given json. Adds references to tags and notebooks."""
        #Iterates over the list of tag-dicts and adds from the paperwork.tags dict
        #Probably problematic
        logger.info('Parsing json note {}:{}'.format(json['id'], json['title']))
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
        logger.info('Parsing json notebook {}:{}'.format(json['id'], json['title']))
        return self.find_notebook(json['id']) or Notebook(json['title'], json['id'])

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
                note.add_tags( [ self.find_tag(tag['title']) for tag in note_json['tags'] ] )
                nb.add_note(note)

    def upload(self):
        """Uploading notebooks and notes to host."""
        logger.info('Uploading all')
        for tag in self.tags:
            self.api.create_tag(tag.to_json())
        for nb in self.notebooks:
            if 'All Notes' in nb.title:
                logger.info('Not uploading notebook {}'.format(nb))
            elif nb.id is 0:
                logger.info('Uploading and creating notebook{}'.format(nb))
                nb.id = self.api.create_notebook(nb.title)['id']
            else:
                logger.info('Uploading notebook {}'.format(nb))
                self.api.update_notebook(nb.to_json())
            for note in nb.notes:
                if note.id is 0:
                    logger.info('Uploading and creating note {}'.format(note))
                    note.id = self.api.create_note(nb.id, note.title, note.content)['id']
                else:
                    logger.info('Uploading note {}'.format(note))
                    self.api.update_note(note.to_json())

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


    def find_tag(self, key):
        """Finds tag with key."""
        for tag in self.tags:
            if key in (tag.id, tag.title):
                return tag

    def find_or_create_tag(self, key):
        """Return tag if found, else return new tag instance."""
        return self.find_tag(key) or self.add_tag(Tag(key))

    def find_notebook(self, key):
        """Find notebook by id."""
        for notebook in self.notebooks:
            if key in (notebook.id, notebook.title):
                return notebook

if __name__ == '__main__':
    import unittest
    testsuite = unittest.TestLoader().discover('./tests/')
    unittest.TextTestRunner(verbosity=1).run(testsuite)
