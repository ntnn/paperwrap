import unittest
from unittest.mock import patch, call
import models

class TestNotebook(unittest.TestCase):
    def setUp(self):
        self.content = 'test content'
        self.id = 10
        self.title = 'a title'
        self.tags = [
                { 'id': 55, 'title': 'tag01' },
                { 'id': 46, 'title': 'tag02' }
                ]
        self.note = {
                'id': self.id,
                'title': self.title,
                'content': self.content,
                'tags': self.tags
                }

    def tearDown(self):
        pass

    def test_creation(self):
        nb = models.Notebook(self.title)
        self.assertEqual(nb.title, self.title)
        self.assertEqual(nb.id, 0)
        self.assertEqual(nb.notes, [])

    @patch('wrapper.list_notebook_notes')
    def test_from_json(self, mocked_request):
        test_json = {
                'title': self.title,
                'id': self.id,
                }
        nb = models.Notebook.from_json(test_json)
        self.assertEqual(nb.title, self.title)
        self.assertEqual(nb.id, self.id)
        self.assertEqual(mocked_request.call_args_list,
                [ call(self.id) ])
        self.assertTrue(mocked_request.called)

    def test_to_json(self):
        test_json = {
                'id': self.id,
                'title': self.title
                }
        self.assertEqual(models.Notebook(self.title, self.id).to_json(),
                test_json)

class TestNote(TestNotebook):
    def test_creation(self):
        test_title = 'note title'
        note = models.Note(test_title)
        self.assertEqual(note.title, test_title)
        self.assertEqual(note.id, 0)
        self.assertEqual(note.content, '')

    def test_from_json(self):
        test_json = {
                'id': self.id,
                'title': self.title,
                'content': self.content,
                'tags': self.tags
                }
        note = models.Note.from_json(test_json, None)
        self.assertEqual(note.content, self.content)
        self.assertEqual(note.id, self.id)
        self.assertEqual(note.title, self.title)

    def test_to_json(self):
        note = models.Note(self.title, self.id)
        note.content = self.content
        note.tags = self.tags
        self.assertEqual(note.to_json(), self.note)


if __name__ == "__main__":
    unittest.main()
