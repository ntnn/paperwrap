import unittest
from paperworks import models

class TestModel(unittest.TestCase):
    def setUp(self):
        self.content = 'test content'
        self.id = 10
        self.title = 'a title'
        self.tags = set( [
                models.Note('tag01', 55),
                models.Note('tag02', 46)
                ])
        self.note = {
                'id': self.id,
                'title': self.title,
                'content': self.content,
                'tags': self.tags
                }
        self.notebook = {
                'id': self.id,
                'title': self.title,
                'type': 0
                }
        self.tag = {
                'id': self.id,
                'title': self.title
                }

    def tearDown(self):
        pass

    def create_test(self, other):
        self.assertEqual(other.title, self.title)
        self.assertEqual(other.id, 0)

    def from_json_test(self, other):
        self.assertEqual(other.title, self.title)
        self.assertEqual(other.id, self.id)

    def to_json_test(self, other):
        self.assertEqual(other['title'], self.title)
        self.assertEqual(other['id'], self.id)

class TestNotebook(TestModel):
    def test_creation(self):
        nb = models.Notebook(self.title)
        self.create_test(nb)
        self.assertEqual(nb.notes, set())

    def test_from_json(self):
        nb = models.Notebook.from_json(self.notebook)
        self.from_json_test(nb)

    def test_to_json(self):
        self.to_json_test(models.Notebook(self.title, self.id).to_json())

class TestNote(TestModel):
    def test_creation(self):
        note = models.Note(self.title)
        self.create_test(note)
        self.assertEqual(note.content, '')

    def test_from_json(self):
        note = models.Note.from_json(self.note)
        self.assertEqual(note.content, self.content)
        self.from_json_test(note)

    # TODO (Nelo Wallus): Throws NoneType error without reason.
    @unittest.expectedFailure
    def test_to_json(self):
        note = models.Note(self.title, self.id, self.content, self.tags,
                models.Notebook.from_json(self.notebook))
        note_json = note.to_json()
        self.test_to_json(note_json)
        self.assertEqual(note_json['content'], self.content)

class TestTag(TestModel):
    def test_creation(self):
        tag = models.Tag(self.title)
        self.create_test(tag)

    def test_to_json(self):
        self.to_json_test(models.Tag(self.title, self.id).to_json())
