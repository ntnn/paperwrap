from urllib.request import Request, urlopen
from urllib.parse import urlencode
from base64 import b64encode
import logging
import json

logger = logging.getLogger('paperwork-wrapper')

host = None
api = '/api/v1/'

headers = None
user_agent = 'paperwork.py v0.1 by ntnn'

api_path = {
        'notebooks':   'notebooks',
        'notebook':    'notebooks/{}',
        'notes':       'notebooks/{}/notes',
        'note':        'notebooks/{}/notes/{}',
        'move':        'notebooks/{}/notes/{}/move/{}',
        'versions':    'notebooks/{}/notes/{}/versions',
        'version':     'notebooks/{}/notes/{}/versions/{}',
        'attachments': 'notebooks/{}/notes/{}/versions/{}/attachments',
        'attachment':  'notebooks/{}/notes/{}/versions/{}/attachments/{}',
        'tags':        'tags',
        'tag':         'tags/{}',
        'tagged':      'tagged/{}',
        'search':      'search/{}',
        'i18n':        'i18n',
        'i18nkey':     'i18n/{}'
        }

def b64(string):
    """Returns given string as base64 hash."""
    return b64encode(string.encode('UTF-8')).decode('ASCII')

def initialize(username, password, uri, user_agent = user_agent):
    """Initialize with the given information."""
    global host, headers
    host = uri
    headers = {
            'Application-Type': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + b64('{}:{}'.format(username, password)),
            'Connection': 'keep-alive',
            'User-Agent': user_agent
            }

def request(data, method, keyword, *args):
    """Sends a request to the host and returns the parsed json data if successfull."""
    try:
        data = json.dumps(data).encode('ASCII')
        uri = host + api + api_path[keyword].format(*args)
        request = Request(uri, data = data, headers = headers)
        request.method = method
        logger.info('{} request to {} with {}'.format(method, uri, data))
        res = urlopen(request)
        json_res = json.loads(res.read().decode('ASCII'))
        if json_res['success'] is False:
            logger.error('Unsuccessful request.')
        else:
            return json_res['response']
    except Exception as e:
        logger.error(e)

def get(keyword, *args):
    """Convenience wrapper for GET request."""
    return request(None, 'GET', keyword, *args)

def post(data, keyword, *args):
    """Convenience wrapper for POST request."""
    return request(data, 'POST', keyword, *args)

def put(data, keyword, *args):
    """Convenience wrapper for PUT request."""
    return request(data, 'PUT', keyword, *args)

def delete(keyword, *args):
    """Convenience wrapper for DELETE request."""
    return request(None, 'DELETE', keyword, *args)

def list_notebooks():
    """Return all notebooks in a list."""
    return get('notebooks')

def create_notebook(name):
    """Create new notebook with name."""
    return post({'type': 0, 'title': name, 'shortcut':''}, 'notebooks')

def get_notebook(notebook_id):
    """Returns notebook."""
    return get('notebook', notebook_id)

def update_notebook(notebook):
    """Updates notebook."""
    return put(notebook, 'notebook', notebook['id'])

def remove_notebook(notebook_id):
    """Deletes notebook and all containing notes."""
    return delete('notebook', notebook_id)

def list_notebook_notes(notebook_id):
    """Returns notes in notebook in a list."""
    return get('notes', notebook_id)

def create_note(notebook_id, note_title, content = ''):
    """Creates note with note_title in notebook. Returns note."""
    return post({'title': note_title, 'content': content}, 'notes', notebook_id)

def get_note(notebook_id, note_id):
    """Returns note with note_id from notebook with notebook_id."""
    return get_notes(notebook_id, [note_id])

def get_notes(notebook_id, note_ids):
    """Returns note with note_id from notebook with notebook_id."""
    return get('note', notebook_id, ','.join([ str(note_id) for note_id in note_ids ]))

def update_note(note):
    """Updates note and returns meta info."""
    return put(note, 'note', note['notebook_id'], note['id'])

def remove_note(note):
    """Deletes note and returns meta info."""
    return remove_notes([note])

def remove_notes(notes):
    """Deletes note and returns meta info."""
    return delete('notes', notes[0]['notebook_id'], ','.join([ note['id'] for note in notes ]))

def move_note(note, new_notebook_id):
    """Moves note to new_notebook_id and returns meta info."""
    return move_notes([note], new_notebook_id)

def move_notes(notes, new_notebook_id):
    """Moves notes to new_notebook_id and returns meta info."""
    return get('move', notes[0]['notebook_id'], ','.join([ note['id'] for note in notes ]), new_notebook_id)

def list_note_versions(note):
    return list_notes_versions([note])

def list_notes_versions(notes):
    return get('versions', notes[0]['notebook_id'], ','.join([ note['id'] for note in notes ]))

def get_note_version(note, version_id):
    return get('version', note['notebook_id'], note['id'], version_id)

def list_note_attachments(note):
    return get('attachments', note['notebook_id'], note['id'], note['versions'][0]['id'])

def get_note_attachment(note, attachment_id):
    return get('attachment', note['notebook_id'], note['id'], note['versions'][0]['id'], attachment_id)

def remove_note_attachment(note, attachment_id):
    return delete('attachment', note['notebook_id'], note['id'], note['versions'][0]['id'], attachment_id)

# TODO (Nelo Wallus): Create method
def upload_attachment(note, attachment):
    pass

def list_tags():
    """Returns all tags."""
    return get('tags')

def get_tag(tag_id):
    """Returns tag with tag_id."""
    return get('tag', tag_id)

def list_tagged(tag_id):
    """Returns notes tagged with tag."""
    return get('tagged', tag_id)

def search(keyword):
    """Search for notes containing given keyword."""
    return get('search', b64(keyword))

def i18n(keyword = None):
    """Returns either the full i18n dict or the requested word."""
    if keyword:
        return get('i18nkey', keyword)
    return get('i18n')

if __name__ == '__main__':
    import unittest
    testsuite = unittest.TestLoader().discover('./tests/')
    unittest.TextTestRunner(verbosity=1).run(testsuite)
