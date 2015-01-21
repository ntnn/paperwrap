#!/usr/bin/env python3
import unittest
from unittest.mock import call, patch
import paperwork as pp

class TestRequests(unittest.TestCase):
    def setUp(self):
        self.patcher = patch('paperwork.request')
        self.mocked_request = self.patcher.start()

        self.notebook_id = '1'
        self.new_notebook_id = '2'
        self.notebook_title = 'notebook title'
        self.notebook = {
                'id': self.notebook_id,
                'title': self.notebook_title
                }
        self.note_title = 'note title'
        self.content = 'some content'
        self.note_id = '2'
        self.version_id = '10'
        self.attachment = ''
        self.attachment_id = '55'
        self.note = {
                'id': self.note_id,
                'title': self.note_title,
                'content': self.content,
                'notebook_id': self.notebook_id,
                'versions':[
                    { 'id': self.version_id }
                    ]
                }
        self.tag_id = '34'
        self.keyword = 'test keyword'
        self.keyword_b64 = 'dGVzdCBrZXl3b3Jk'

        self.user = 'testuser'
        self.passwd = 'testpassword'
        self.uri = 'test/uri'
        self.agent = 'dummy agent'

    def tearDown(self):
        self.patcher.stop()

    def test_b64(self):
        self.assertEqual(pp.b64(self.keyword), self.keyword_b64)

    def test_initialize(self):
        pp.initialize(self.user, self.passwd, self.uri, self.agent)
        self.assertEqual(pp.host, self.uri)
        self.assertEqual(pp.headers['User-Agent'], self.agent)
        self.assertEqual(pp.headers['Authorization'], 'Basic ' + pp.b64('{}:{}'.format(self.user, self.passwd)))

    def asserts(self, response, *args):
        self.assertTrue(self.mocked_request.called)
        self.assertEqual(self.mocked_request.call_args_list, [call(*args)])
        self.assertEqual(self.mocked_request.return_value, response)

    def get_asserts(self, response, *args):
        self.asserts(response, None, 'GET', *args)

    def post_asserts(self, response, data, *args):
        self.asserts(response, data, 'POST', *args)

    def put_asserts(self, response, data, *args):
        self.asserts(response, data, 'PUT', *args)

    def delete_asserts(self, response, *args):
        self.asserts(response, None, 'DELETE', *args)

    #actual tests
    def test_list_notebooks(self):
        self.get_asserts(pp.list_notebooks(),
            'notebooks')

    def test_create_notebook(self):
        data = {
                'type': 0,
                'title': self.notebook_title,
                'shortcut': ''
                }
        self.post_asserts(pp.create_notebook(self.notebook_title),
            data, 'notebooks')

    def test_get_notebook(self):
        self.get_asserts(pp.get_notebook(self.notebook_id),
            'notebook', self.notebook_id)

    def test_update_notebook(self):
        response = pp.update_notebook(self.notebook)
        self.put_asserts(response, self.notebook, 'notebook', self.notebook_id)

    def test_remove_notebook(self):
        self.delete_asserts(pp.remove_notebook(self.notebook_id),
            'notebook', self.notebook_id)

    def test_list_notebook_notes(self):
        self.get_asserts(pp.list_notebook_notes(self.notebook_id),
            'notes', self.notebook_id)

    def test_create_note(self):
        data = {'title': self.note_title, 'content': self.content}
        self.post_asserts(pp.create_note(self.notebook_id, self.note_title, self.content),
            data, 'notes', self.notebook_id)

    def test_get_note(self):
        self.get_asserts(pp.get_note(self.notebook_id, self.note_id),
            'note', self.notebook_id, self.note_id)

    def test_get_notes(self):
        self.get_asserts(pp.get_notes(self.notebook_id, [self.note_id]),
            'note', self.notebook_id, self.note_id)

    def test_update_note(self):
        self.put_asserts(pp.update_note(self.note),
            self.note, 'note', self.notebook_id, self.note_id)

    def test_remove_note(self):
        self.delete_asserts(pp.remove_note(self.note),
            'notes', self.notebook_id, self.note_id)

    def test_remove_notes(self):
        self.delete_asserts(pp.remove_notes([self.note]),
            'notes', self.notebook_id, self.note_id)

    def test_move_note(self):
        self.get_asserts(pp.move_note(self.note, self.new_notebook_id),
            'move', self.notebook_id, self.note_id, self.new_notebook_id)

    def test_move_notes(self):
        self.get_asserts(pp.move_notes([self.note], self.new_notebook_id),
            'move', self.notebook_id, self.note_id, self.new_notebook_id)

    def test_list_note_versions(self):
        self.get_asserts(pp.list_note_versions(self.note),
            'versions', self.notebook_id, self.note_id)

    def test_list_notes_versions(self):
        self.get_asserts(pp.list_notes_versions([self.note]),
            'versions', self.notebook_id, self.note_id)

    def test_get_note_version(self):
        self.get_asserts(pp.get_note_version(self.note, self.version_id),
            'version', self.notebook_id, self.note_id, self.version_id)

    def test_list_note_attachments(self):
        self.get_asserts(pp.list_note_attachments(self.note),
            'attachments', self.notebook_id, self.note_id, self.version_id)

    def test_get_note_attachment(self):
        self.get_asserts(pp.get_note_attachment(self.note, self.attachment_id),
            'attachment', self.notebook_id, self.note_id, self.version_id, self.attachment_id)

    def test_remove_note_attachment(self):
        self.delete_asserts(pp.remove_note_attachment(self.note, self.attachment_id),
            'attachment', self.notebook_id, self.note_id, self.version_id, self.attachment_id)

    def test_upload_attachment(self):
        self.post_asserts(pp.upload_attachment(self.note, self.attachment),
            self.attachment, 'attachments', self.notebook_id, self.note_id, self.version_id)

    def test_list_tags(self):
        self.get_asserts(pp.list_tags(),
            'tags')

    def test_get_tag(self):
        self.get_asserts(pp.get_tag(self.tag_id),
            'tag', self.tag_id)

    def test_list_tagged(self):
        self.get_asserts(pp.list_tagged(self.tag_id),
            'tagged', self.tag_id)

    def test_search(self):
        self.get_asserts(pp.search(self.keyword),
            'search', pp.b64(self.keyword))

    def test_i18n(self):
        self.get_asserts(pp.i18n(),
            'i18n')

    def test_i18n_param(self):
        self.get_asserts(pp.i18n(self.keyword),
            'i18nkey', self.keyword)

if __name__ == "__main__":
    unittest.main()
