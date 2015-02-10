import unittest
from json import dumps
from paperworks import models
from test_data import *

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


class TestPaperwork(unittest.TestCase):
    def setUp(self):
        self.patcher = patch('paperworks.wrapper.requests.request')
        self.mocked_request = self.patcher.start()
        temp = ResponseObj(dumps({
            'success': True,
            'response': 'success'
            }))
        self.mocked_request.return_value = temp
        self.pw = models.Paperwork(uri)
        self.api = self.pw.api

    def tearDown(self):
        pass

    @patch('paperworks.wrapper.API.list_note_attachments')
    @patch('paperworks.wrapper.API.list_notebook_notes')
    @patch('paperworks.wrapper.API.list_notebooks')
    @patch('paperworks.wrapper.API.list_tags')
    def test_download(self, mocked_list_tags, mocked_list_notebooks,
                      mocked_list_notebook_notes,
                      mocked_list_note_attachments):
        mocked_list_tags.return_value = tags
        mocked_list_notebooks.return_value = [notebook]
        mocked_list_notebook_notes.return_value = notes
        mocked_list_note_attachments.return_value = attachments
        self.pw.download()
        self.assertTrue(mocked_list_tags.called)
        self.assertTrue(mocked_list_notebooks.called)
        self.assertTrue(mocked_list_notebook_notes.called)
        self.assertTrue(mocked_list_note_attachments.called)

    @patch('paperworks.models.Note.update')
    @patch('paperworks.models.Notebook.update')
    def test_update(self, mocked_update_notebook, mocked_update_note):
        parsed_notebook = models.Notebook.from_json(self.api, notebook)
        self.pw.add_notebook(parsed_notebook)
        self.pw.add_tag(models.Tag.from_json(self.api, tag))
        parsed_notebook.add_note(models.Note.from_json(parsed_notebook, note))
        self.pw.update()
        self.assertTrue(mocked_update_note.called)
        self.assertTrue(mocked_update_notebook.called)

    def test_get_notes(self):
        nb = models.Notebook.from_json(self.api, notebook)
        nb2 = models.Notebook.from_json(self.api, notebook2)
        n = models.Note.from_json(nb, note)
        nb.add_note(n)
        n2 = models.Note.from_json(nb2, note2)
        nb2.add_note(n2)
        self.pw.add_notebook(nb)
        self.pw.add_notebook(nb2)
        nb_notes = self.pw.get_notes()
        self.assertTrue(n in nb_notes)
        self.assertTrue(n2 in nb_notes)


class TestModel(unittest.TestCase):
    def setUp(self):
        self.patcher = patch('paperworks.wrapper.requests.request')
        self.mocked_request = self.patcher.start()
        temp = ResponseObj(dumps({
            'success': True,
            'response': 'success'
            }))
        self.mocked_request.return_value = temp
        self.api = models.Paperwork(uri).api

    def tearDown(self):
        pass

    def from_json_test(self, model, title, ident):
        self.assertEqual(model.title, title)
        self.assertEqual(model.ident, ident)

    def to_json_test(self, model, title, ident):
        self.assertEqual(model['title'], title)
        self.assertEqual(model['id'], ident)


class TestNotebook(TestModel):
    def setUp(self):
        super().setUp()
        self.nb = models.Notebook(
            notebook_title,
            notebook_id,
            self.api)
        self.note = models.Note.from_json(self.nb, note)

    def test_to_json(self):
        self.to_json_test(
            models.Notebook(notebook_title, notebook_id, self.api).to_json(),
            notebook_title,
            notebook_id)

    def test_from_json(self):
        parsed_notebook = models.Notebook.from_json(self.api, notebook)
        self.from_json_test(parsed_notebook, notebook_title, notebook_id)

    @patch('paperworks.wrapper.API.create_notebook')
    def test_create(self, mocked_create_notebook):
        models.Notebook.create(self.api, notebook_title)
        mocked_create_notebook.assert_called_with(notebook_title)

    @patch('paperworks.wrapper.API.delete_notebook')
    def test_delete(self, mocked_delete):
        self.nb.delete()
        mocked_delete.assert_called_with(notebook_id)

    @patch('paperworks.wrapper.API.create_notebook')
    @patch('paperworks.wrapper.API.get_notebook')
    @patch('paperworks.wrapper.API.update_notebook')
    def test_update_updates_remote(self, mocked_update, mocked_get,
                                   mocked_create):
        mocked_get.return_value = note
        self.nb.update()
        self.assertFalse(mocked_create.called)
        mocked_get.assert_called_with(self.nb.ident)
        mocked_update.assert_called_with(self.nb.to_json())


    def test_get_notes(self):
        self.nb.add_note(self.note)
        notes = self.nb.get_notes()
        notes[0] = self.note

    @patch('paperworks.wrapper.API.create_note')
    def test_create_note(self, mocked_create_note):
        self.nb.create_note(note_title)
        mocked_create_note.assert_called_with(self.nb.ident, note_title)

    def test_add_note(self):
        self.nb.add_note(self.note)
        self.assertTrue(self.note in self.nb.notes.values())
        self.assertEqual(self.note.notebook, self.nb)

    @patch('paperworks.wrapper.API.list_notebook_notes')
    def test_download(self, mocked_list_notebook_notes):
        mocked_list_notebook_notes.return_value = []
        self.nb.download([models.Tag.from_json(self.api, tag)])
        self.assertTrue(mocked_list_notebook_notes.called)


class TestNote(TestModel):
    def setUp(self):
        super().setUp()
        self.notebook = models.Notebook.from_json(self.api, notebook)
        self.new_note = models.Note(note_title, note_id, self.notebook)
        self.old_note = models.Note(
            note_title,
            note_id,
            self.notebook,
            content)
        self.parsed_note = models.Note.from_json(self.notebook, note)
        self.notebook.add_note(self.parsed_note)
        self.parsed_note_json = self.parsed_note.to_json()

    def test_to_json(self):
        self.old_note.add_tags([models.Tag.from_json(self.api, tag)])
        self.notebook.add_note(self.old_note)
        json_note = self.old_note.to_json()
        self.assertEqual(json_note['content'], content)
        self.to_json_test(json_note, note_title, note_id)

    def test_from_json(self):
        self.assertEqual(self.parsed_note.content, content)
        self.from_json_test(self.parsed_note, note_title, note_id)

    @patch('paperworks.wrapper.API.create_note')
    def test_create(self, mocked_create_note):
        mocked_create_note.return_value = note
        models.Note.create(note_title, self.notebook)
        mocked_create_note.assert_called_with(notebook_id, note_title)

    @patch('paperworks.wrapper.API.move_note')
    def test_move_to(self, mocked_move):
        self.parsed_note.move_to(
            models.Notebook.from_json(
                self.api, notebook2))
        mocked_move.assert_called_with(self.parsed_note_json, notebook2_id)

    @patch('paperworks.wrapper.API.delete_note')
    def test_delete(self, mocked_delete):
        self.parsed_note.delete()
        mocked_delete.assert_called_with(self.parsed_note.to_json())

    @patch('paperworks.wrapper.API.create_note')
    @patch('paperworks.wrapper.API.get_note')
    @patch('paperworks.wrapper.API.update_note')
    def test_update_remote(self, mocked_update, mocked_get, mocked_create):
        mocked_get.return_value = note
        self.parsed_note.updated_at = '2014-09-22 19:43:59'
        self.parsed_note.update()
        self.assertFalse(mocked_create.called)
        mocked_get.assert_called_with(
            self.parsed_note.notebook.ident,
            self.parsed_note.ident)
        mocked_update.assert_called_with(self.parsed_note.to_json())

    @patch('paperworks.wrapper.API.create_note')
    @patch('paperworks.wrapper.API.get_note')
    @patch('paperworks.wrapper.API.update_note')
    def test_update_local(self, mocked_update, mocked_get, mocked_create):
        mocked_get.return_value = note
        self.parsed_note.updated_at = '2014-09-14 19:43:59'
        self.parsed_note.update()
        self.assertFalse(mocked_create.called)
        mocked_get.assert_called_with(
            self.parsed_note.notebook.ident,
            self.parsed_note.ident)
        self.assertFalse(mocked_update.called)
        self.assertEqual(self.parsed_note.title, note['title'])
        self.assertEqual(self.parsed_note.content, note['content'])
        self.assertEqual(self.parsed_note.updated_at, note['updated_at'])


class TestTag(TestModel):
    def test_to_json(self):
        self.to_json_test(models.Tag(tag_title, tag_id, self.api).to_json(),
                          tag_title, tag_id)

    def test_from_json(self):
        self.tag = models.Tag.from_json(self.api, tag)
        self.assertEqual(tag['id'], self.tag.ident)
        self.assertEqual(tag['title'], self.tag.title)
        self.assertEqual(tag['visibility'], self.tag.visibility)
