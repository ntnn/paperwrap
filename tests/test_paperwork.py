#!/usr/bin/env python3
import unittest
from unittest.mock import patch, call
import paperwork
import pdb

class TestPaperwork(unittest.TestCase):
    def setUp(self):
        self.notebook1 = {
                'title': 'notebook 01',
                'id': 1
                }
        self.notebook2 = {
                'title': 'notebook 02',
                'id': 2
                }
        self.tag1 = {
                'title': 'tag 01',
                'id': 3,
                'visibility': 0
                }
        self.tag2 = {
                'title': 'tag 02',
                'id': 4,
                'visibility': 0
                }
        self.tags = {
                self.tag1['id']: self.tag1,
                self.tag2['id']: self.tag2
                }
        self.note1 = {
                'title': 'note 1',
                'id': 5,
                'content': 'note 1 content',
                'tags': [ self.tag1 ],
                'notebook_id': self.notebook1['id']
                }
        self.note2 = {
                'title': 'note 2',
                'id': 6,
                'content': 'note 2 content',
                'tags': [ self.tag2 ],
                'notebook_id': self.notebook2['id']
                }
        self.pw = paperwork.Paperwork('user', 'passwd')

    def tearDown(self):
        pass

    def test_parse_json_tag(self):
        tag = self.pw.parse_json_tag(self.tag1)
        self.assertEqual(tag.id, self.tag1['id'])
        self.assertEqual(tag.title, self.tag1['title'])
        self.assertEqual(tag.visibility, self.tag1['visibility'])

    def test_parse_json_note(self):
        tag = self.pw.parse_json(self.tag1)
        self.pw.add_tag(tag)
        self.pw.add_notebook(self.pw.parse_json_notebook(self.notebook1))
        note = self.pw.parse_json_note(self.note1)
        note.add_tag(tag)
        self.assertEqual(note.id, self.note1['id'])
        self.assertEqual(note.title, self.note1['title'])
        self.assertTrue(self.pw.find_tag(tag.title) in note.tags)
        self.assertEqual(note.notebook.id, self.note1['notebook_id'])

    def test_parse_json_notebook(self):
        nb = self.pw.parse_json_notebook(self.notebook1)
        self.assertEqual(nb.id, self.notebook1['id'])
        self.assertEqual(nb.title, self.notebook1['title'])

    @patch('wrapper.list_tags')
    @patch('wrapper.list_notebooks')
    @patch('wrapper.list_notebook_notes')
    def test_download(self, mocked_list_tags, mocked_list_notebooks, mocked_list_notebook_notes):
        mocked_list_tags.return_value( [self.tag1, self.tag2] )
        mocked_list_notebooks( [self.notebook1, self.notebook2] )
        mocked_list_notebook_notes( [self.note1, self.note2] )
        self.pw.download()
        mocked_list_tags.assert_called()
        mocked_list_notebooks.assert_called()
        mocked_list_notebook_notes.assert_called()

    @patch('wrapper.update_notebook')
    @patch('wrapper.update_note')
    def test_upload(self, mocked_update_notebook, mocked_update_note):
        nb = self.pw.parse_json(self.notebook1)
        self.pw.add_notebook(nb)
        self.pw.add_tag(self.pw.parse_json(self.tag1))
        nb.add_note(self.pw.parse_json(self.note1))
        self.pw.upload()
        mocked_update_notebook.assert_called()
        mocked_update_note.assert_called()

if __name__ == "__main__":
    unittest.main()
