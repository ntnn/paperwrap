#!/usr/bin/env python3
import unittest
from .test_data import *
from ..paperworks.models import Notebook, Note, Tag, Attachment
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

patch('paperworks.wrapper.API.test_connection', lambda x: True).start()
patch('builtins.input', lambda x: 'test/uri').start()
from paperworks import cli


class TestCli(unittest.TestCase):
    def setUp(self):
        cli.PW.notebooks = {
            notebook['id']: Notebook.from_json(cli.PW.api, notebook)
            for notebook in notebooks}
        for notebook in cli.PW.notebooks.values():
            for note in notes:
                note = Note.from_json(notebook, note)
                note.attachments = [
                    Attachment.from_json(note, attachment)
                    for attachment in attachments
                    ]
                notebook.notes[note.ident] = note
        cli.PW.tags = {
            tag['id']: Tag.from_json(cli.PW.api, tag)
            for tag in tags
            }

    def tearDown(self):
        pass

    @patch('paperworks.models.Paperwork.download')
    def test_download(self, mocked_download):
        cli.download()
        self.assertTrue(mocked_download.called)

    @patch('paperworks.models.Paperwork.update')
    def test_update(self, mocked_update):
        cli.update()
        self.assertTrue(mocked_update.called)

    @patch('builtins.print')
    def test_print_all(self, mocked_print):
        cli.print_all()
        self.assertTrue(mocked_print.called)

    def test_split(self):
        first, second = cli.split('first and second', ' and ')
        self.assertEqual(first, 'first')
        self.assertEqual(second, 'second')

    def test_split_none(self):
        first, second = cli.split('first and second', ' none ')
        self.assertEqual(first, None)
        self.assertEqual(second, 'first and second')

    def test_split_args_all(self):
        att, note, notebook = cli.split_args('attach to note in notebook')
        self.assertEqual(att, 'attach')
        self.assertEqual(note, 'note')
        self.assertEqual(notebook, 'notebook')

    def test_split_args_note_nb(self):
        att, note, notebook = cli.split_args('note in notebook')
        self.assertEqual(att, None)
        self.assertEqual(note, 'note')
        self.assertEqual(notebook, 'notebook')

    @patch('builtins.input', lambda x: '')
    def test_prompt_true(self):
        self.assertTrue(cli.prompt('true'))

    @patch('builtins.input', lambda x: '')
    def test_prompt_false(self):
        self.assertFalse(cli.prompt('false', important=True))

    def test_split_and_search_args_all(self):
        att, note, notebook = cli.split_and_search_args(
            'attched.pdf to note in notebook')
        self.assertEqual(att.title, 'attached.pdf')
        self.assertEqual(note.title, 'note title')
        self.assertEqual(notebook.title, 'notebook title')

    def test_split_and_search_args_note_nb(self):
        att, note, notebook = cli.split_and_search_args(
            'note in notebook')
        self.assertEqual(att, None)
        self.assertEqual(note.title, 'note title')
        self.assertEqual(notebook.title, 'notebook title')

    @patch('paperworks.cli.prompt', lambda x: True)
    @patch('paperworks.models.Attachment.delete')
    def test_delete_attachment(self, mocked_delete):
        cli.delete('attached.pdf to note in notebook')
        self.assertTrue(mocked_delete.called)

    @patch('paperworks.cli.prompt', lambda x: True)
    @patch('paperworks.models.Note.delete')
    def test_delete_note(self, mocked_delete):
        cli.delete('note in notebook')
        self.assertTrue(mocked_delete.called)

    @patch('paperworks.cli.prompt', lambda x: True)
    @patch('paperworks.models.Notebook.delete')
    def test_delete_notebook(self, mocked_delete):
        cli.delete('notebook')
        self.assertTrue(mocked_delete.called)

    @patch('paperworks.cli.prompt', lambda x: True)
    @patch('paperworks.models.Note.move_to')
    def test_move(self, mocked_move):
        cli.move('note in notebook to notebook')
        self.assertTrue(mocked_move.called)

    @patch('paperworks.cli.prompt', lambda x: True)
    @patch('paperworks.models.Notebook.create_note')
    def test_create_note(self, mocked_create):
        cli.create('testnote in notebook')
        self.assertTrue(mocked_create.called)

    @patch('paperworks.cli.prompt', lambda x: True)
    @patch('paperworks.models.Paperwork.create_notebook')
    def test_create_notebook(self, mocked_create):
        cli.create('testnotebook')
        self.assertTrue(mocked_create.called)

    @patch('builtins.print')
    def test_tags(self, mocked_print):
        cli.tags()
        self.assertTrue(mocked_print.called)

    @patch('paperworks.cli.prompt', lambda x: True)
    @patch('paperworks.models.Note.add_tags')
    def test_tag_to_note(self, mocked_add_tags):
        cli.tag('note in notebook with tag')
        self.assertTrue(mocked_add_tags.called)

    @patch('paperworks.cli.prompt', lambda x: True)
    @patch('paperworks.models.Paperwork.add_tag')
    def test_tag(self, mocked_add_tag):
        cli.tag('tag01')
        self.assertTrue(mocked_add_tag.called)

    @patch('builtins.print')
    def test_tagged(self, mocked_print):
        cli.tagged('something')
        self.assertTrue(mocked_print.called)

    @patch('paperworks.models.Note.upload_file')
    def test_upload(self, mocked_upload):
        cli.upload('testfile to note in notebook')
        self.assertTrue(mocked_upload.called_with('testfile'))


if __name__ == "__main__":
    unittest.main()
