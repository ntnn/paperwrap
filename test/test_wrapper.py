# License: MIT
# Author: Nelo Wallus, http://github.com/ntnn
import unittest
from paperwrap import wrapper
from json import dumps
from test_data import *

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


class TestAPI(unittest.TestCase):
    def setUp(self):
        self.patcher = patch('paperwrap.wrapper.requests.request')
        self.mocked_request = self.patcher.start()
        temp = ResponseObj(dumps({
            'success': True,
            'response': 'success'
            }))
        self.mocked_request.return_value = temp
        self.mocked_request.return_value = temp
        self.api = wrapper.API(uri, agent)

    def tearDown(self):
        self.patcher.stop()

    def test_b64(self):
        self.assertEqual(wrapper.b64(keyword), keyword_b64)

    def test_init(self):
        self.assertEqual(self.api.host, uri_correct)
        self.assertEqual(self.api.headers['User-Agent'], agent)

    def request(self, function, keyword, *args):
        temp = ResponseObj(dumps({
            'success': True,
            'response': ret[keyword]
            }))
        self.mocked_request.return_value = temp

        response = function(*args)

        self.mocked_request.assert_called()
        self.assertEqual(response, ret[keyword])

    def test_list_notebooks(self):
        self.request(self.api.list_notebooks, 'notebooks')

    def test_create_notebook(self):
        self.request(self.api.create_notebook, 'notebooks', notebook_title)

    def test_get_notebook(self):
        self.request(self.api.get_notebook, 'notebook', notebook_id)

    def test_update_notebook(self):
        self.request(self.api.update_notebook, 'notebook', notebook)

    def test_delete_notebook(self):
        self.request(self.api.delete_notebook, 'notebook', notebook_id)

    def test_list_notebook_notes(self):
        self.request(self.api.list_notebook_notes, 'notes', notebook_id)

    def test_create_note(self):
        self.request(self.api.create_note, 'notes', notebook_id,
                     note_title, content)

    def test_get_note(self):
        self.request(self.api.get_note, 'note', notebook_id, note_id)

    def test_get_notes(self):
        self.request(self.api.get_notes, 'note', notebook_id, notes)

    def test_update_note(self):
        self.request(self.api.update_note, 'note', note)

    @patch('paperwrap.wrapper.API.delete_notes')
    def test_delete_note(self, mocked_delete_notes):
        self.api.delete_note(note)
        mocked_delete_notes.assert_called_with([note])

    def test_delete_notes(self):
        self.request(self.api.delete_notes, 'notes', notes)

    @patch('paperwrap.wrapper.API.move_notes')
    def test_move_note(self, mocked_move_notes):
        self.api.move_note(note, new_notebook_id)
        mocked_move_notes.assert_called_with([note], new_notebook_id)

    def test_move_notes(self):
        self.request(self.api.move_notes, 'move', notes, new_notebook_id)

    def test_list_note_versions(self):
        self.request(self.api.list_note_versions, 'versions', note)

    def test_list_notes_versions(self):
        self.request(self.api.list_notes_versions, 'versions', notes)

    def test_get_note_version(self):
        self.request(self.api.get_note_version, 'version', note, version_id)

    def test_list_note_attachments(self):
        self.request(self.api.list_note_attachments, 'attachments', note)

    def test_get_note_attachment(self):
        self.request(self.api.get_note_attachment, 'attachment', note,
                     attachment_id)

    def test_delete_note_attachment(self):
        self.request(self.api.delete_note_attachment, 'attachment', note,
                     attachment_id)

    @patch('paperwrap.wrapper.requests.post')
    @patch('builtins.open', lambda path, mode: path)
    def test_upload_attachment(self, mocked_post):
        self.api.upload_attachment(note, 'some/path/')
        mocked_post.assert_called_with(
            self.api.host + wrapper.API_VERSION +
            wrapper.API_PATH['attachments'].format(
                note['notebook_id'],
                note['id'],
                0),
            files={'file': 'some/path/'},
            headers=self.api.headers
            )

    def test_list_tags(self):
        self.request(self.api.list_tags, 'tags')

    def test_get_tag(self):
        self.request(self.api.get_tag, 'tag', tag_id)

    def test_list_tagged(self):
        self.request(self.api.list_tagged, 'tagged', tag_id)

    def test_search(self):
        self.request(self.api.search, 'search', keyword)

    def test_i18n(self):
        self.request(self.api.i18n, 'i18n')

    def test_i18n_param(self):
        self.request(self.api.i18n, 'i18nkey', keyword)
