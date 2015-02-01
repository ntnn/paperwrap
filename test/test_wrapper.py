# License: MIT
# Author: Nelo Wallus, http://github.com/ntnn
import unittest
from paperworks import wrapper
from json import dumps
import tempfile
from test_data import *

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


class TestRequests(unittest.TestCase):
    def setUp(self):
        self.patcher = patch('paperworks.wrapper.urlopen')
        self.mocked_urlopen = self.patcher.start()
        temp = tempfile.TemporaryFile()
        temp.write(dumps(
            {
                'success': True,
                'response': 'success'
            }).encode('ASCII'))
        temp.seek(0)
        self.mocked_urlopen.return_value = temp
        self.api = wrapper.api(agent)
        self.api.basic_authentication(uri, user, passwd)

    def tearDown(self):
        self.patcher.stop()

    def test_b64(self):
        self.assertEqual(wrapper.b64(keyword), keyword_b64)

    def test_init(self):
        self.assertEqual(self.api.host, uri_correct)
        self.assertEqual(self.api.headers['User-Agent'], agent)
        self.assertEqual(self.api.headers['Authorization'], 'Basic ' + upasswd)

    def request(self, function, keyword, *args):
        temp = tempfile.TemporaryFile()
        temp.write(dumps(
            {
                'success': True,
                'response': ret[keyword]
            }).encode('ASCII'))
        temp.seek(0)
        self.mocked_urlopen.return_value = temp

        response = function(*args)

        temp.close()

        self.mocked_urlopen.assert_called()
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

    def test_delete_note(self):
        self.request(self.api.delete_note, 'notes', note)

    def test_delete_notes(self):
        self.request(self.api.delete_notes, 'notes', notes)

    def test_move_note(self):
        self.request(self.api.move_note, 'move', note, new_notebook_id)

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

    # TODO (Nelo Wallus): Fix actual method
    @unittest.expectedFailure
    def test_upload_attachment(self):
        self.request(self.api.upload_attachment, 'attachments', note,
                     attachment)

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


